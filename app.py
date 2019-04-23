from flask import Flask, redirect, render_template, jsonify, request
from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from forms import LoginForm, NewUserForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = 'Secret'

@app.route('/')
def index_page():
    return redirect('/register')


@app.route('/register', methods=["GET", "POST"])
def registration_form():
    form = NewUserForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data
        email = form.email.data

        pw = User.hashed_pw(username=username, pwd=password)
        user = User(first_name=first_name, last_name=last_name,
                    username=username, password=pw.password, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect('/secrets')

    else:
        return render_template('new_user_form.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_form():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.login(username=username, pwd=password)
        if user:
            return redirect('/secrets')
        else: 
            return redirect('/login')
    else:
        return render_template('login.html', form=form)



@app.route('/secrets')
def secrets():
    return 'You have made it'