from flask import Flask, redirect, render_template, jsonify, request, session
from models import db, connect_db, User, Feedback
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from forms import LoginForm, NewUserForm, FeedbackForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = 'Secret'
app.secret_key = "SHHHHHHHHHHH SEEKRIT"

debug = DebugToolbarExtension(app)


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
        session['user_id'] = username
        return redirect(f'/users/{username}')

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
            session['user_id'] = username
            return redirect(f'/users/{username}')
        else:
            return redirect('/login')
    else:
        return render_template('login.html', form=form)


@app.route('/users/<username>')
def secrets(username):
    if session.get('user_id'):
        user = User.query.get_or_404(session['user_id'])
        feedback = Feedback.query.filter(username == session['user_id'])
        return render_template('userPage.html', user=user, fb=feedback)
    else:
        return redirect('/register')


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if session['user_id'] == username:
        session.pop('user_id')
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/logout')


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def create_feedback(username):
    form = FeedbackForm()
    if form.validate_on_submit() and username == session['user_id']:
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content,
                            username=session['user_id'])
        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{username}')

    else:
        return render_template('feedbackForm.html', form=form, 
                               username=username)


@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)
    if not (feedback.username == session['user_id']):
        return redirect('/login')
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback.title = title
        feedback.content = content

        db.session.commit()
        return redirect(f'/users/{feedback.username}')

    else:
        return render_template('feedbackUpdate.html', form=form,
                               id=feedback_id)

