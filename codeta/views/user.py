"""
    Views that manage a user's account.

    Includes login/logout, join, user homepage, account settings,
    etc.

"""

from flask import (request, session, g, redirect, url_for,
        abort, render_template, flash)

from flask.ext.login import (current_user, login_required,
        login_user, logout_user, confirm_login,
        fresh_login_required)

from codeta import app, auth, login_manager, logger
from codeta.forms.registration import RegistrationForm
from codeta.forms.user_settings import UserNameForm, UserEmailForm, UserPwForm
from codeta.forms.login import LoginForm
from codeta.models.user import User

@app.route('/join', methods=['GET', 'POST'])
def join():
    """ Register the user for an account """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(-1,
                request.form['username'],
                request.form['password'],
                request.form['email'],
                request.form['fname'],
                request.form['lname'])
        rc = user.create()

        return redirect(url_for('login'))
    return render_template('user/join.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm()
    if form.validate_on_submit():
        user = User.auth_user(
                request.form['username'],
                request.form['password'])
        if user:
            login_user(user)
            logger.info('User: %s - login auth success.' % (request.form['username']))
            return redirect(url_for('homepage'))
        else:
            logger.info('User: %s - login auth failure.' % (request.form['username']))
            error = 'Invalid username or password.'

    return render_template('user/login.html', form=form, error=error)

@app.route('/<username>/')
def user_home(username):
    """
        GET - Show the courses the user is enrolled in.
            If g.user = username, provide links to add course
    """
    u = User(None, username, None, None, None, None)
    courses = u.get_courses()

    return render_template('user/home.html', courses=courses, username=username)

@app.route('/<username>/settings')
@login_required
def user_settings(username):
    """
        GET - Show g.user settings
    """
    if g.user.username == username:
        user_data = {
            'fname': g.user.fname,
            'lname': g.user.lname,
            'email': g.user.email
        }
        return render_template('user/settings/settings.html', user_data=user_data, username=username)
    else:
        # unauth user
        return redirect(url_for('user_settings', username=g.user.username))

@app.route('/<username>/settings/name', methods=['GET', 'POST'])
@login_required
def user_setting_name(username):
    """
        GET - Show form for changing g.user first and last name

        POST - Change the name in g.user and in the database
    """
    if g.user.username == username:
        form = UserNameForm()
        if form.validate_on_submit():
            if request.form['fname']:
                g.user.fname = request.form['fname']
            if request.form['lname']:
                g.user.lname = request.form['lname']
            g.user.update()
            return redirect(url_for('user_settings', username=g.user.username))
        else:
            return render_template('user/settings/name.html', username=g.user.username, form=form)
    else:
        # unauthorized user
        return redirect(url_for('user_settings', username=g.user.username))

@app.route('/<username>/settings/email', methods=['GET', 'POST'])
@login_required
def user_setting_email(username):
    """
        GET - Show form for changing g.user email

        POST - Change the email in g.user and in the database
    """
    if g.user.username == username:
        form = UserEmailForm()
        if form.validate_on_submit():
            g.user.email = request.form['email']
            g.user.update()
            return redirect(url_for('user_settings', username=g.user.username))
        else:
            return render_template('user/settings/email.html', username=g.user.username, form=form)
    else:
        # unauthorized user
        return redirect(url_for('user_settings', username=g.user.username))

@app.route('/<username>/settings/password', methods=['GET', 'POST'])
@fresh_login_required
def user_setting_password(username):
    """
        GET - Show password change form

        POST - Update g.user.password to password hash and change it in database
    """
    if g.user.username == username:
        form = UserPwForm()
        if form.validate_on_submit():
            pw_hash = auth.hash_password(request.form['password'])
            if pw_hash:
                g.user.password = pw_hash
                g.user.update()
            return redirect(url_for('user_settings', username=g.user.username))
        else:
            return render_template('user/settings/password.html', username=g.user.username, form=form)
    else:
        # unauthorized user
        return redirect(url_for('user_settings', username=g.user.username))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('user/logout.html')
