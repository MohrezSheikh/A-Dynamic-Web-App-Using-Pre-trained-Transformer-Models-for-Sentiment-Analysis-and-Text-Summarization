from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import hugg
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = 'Your Secret Key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Your path for your database'
SQLALCHEMY_TRACK_MODIFICATIONS = False
API_TOKEN = 'Your API TOKEN from huggingface.co'

Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarization')
def my_forma():
    return render_template('summarization.html')

@app.route('/summarization', methods=['POST'])
def summarization():
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
	    response = requests.post(API_URL, headers=headers, json=payload)
	    return response.json()
	
    text = request.form['text']
    processed_text = query({
	        "inputs": f"{text}",
        })
    return jsonify(processed_text)

@app.route('/sentiment')
def my_form():
    return render_template('sentiment.html')

@app.route('/sentiment', methods=['POST'])
def sentiment():
    API_URL = "https://api-inference.huggingface.co/models/siebert/sentiment-roberta-large-english"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
	        response = requests.post(API_URL, headers=headers, json=payload)
	        return response.json()

    
     
            
    text = request.form['text']
    processed_text = query({
	        "inputs": f"{text}",
        })
    return jsonify(processed_text)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))

        return 'Invalid username or password!'

    return render_template('login.html', form=form)
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h2>new user has been created!</h2>'

    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)