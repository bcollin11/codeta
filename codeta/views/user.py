"""
    Contains views that users directly access.

    Includes login/logout, homepage, account management,
    etc.

"""

from flask import request, session, g, redirect, url_for, \
        abort, render_template, flash

from flask.ext.login import (current_user, login_required,
        login_user, logout_user, confirm_login,
        fresh_login_required)

from codeta import app, login_manager, logger
from codeta.forms.registration import RegistrationForm
from codeta.forms.course import CourseCreateForm
from codeta.forms.login import LoginForm
from codeta.models.course import Course

@app.route('/')
def homepage():
    return render_template('codeta/home.html')

@app.route('/join', methods=['GET', 'POST'])
def join():
    """ Register the user for an account """
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        rc = app.db.register_user(
                request.form['username'],
                request.form['password'],
                request.form['email'],
                request.form['fname'],
                request.form['lname'])

        return redirect(url_for('login'))
    return render_template('user/join.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = app.db.auth_user(
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
        User's homepage. Displays things about their courses
        and current assignments
    """
    # lookup the <username>'s courses
    form = CourseCreateForm(request.form)
    courses=None
    if g.user.is_authenticated():
        courses = g.user.get_courses()
    return render_template('user/home.html', form=form, courses=courses)

@app.route('/<username>/add', methods=['POST'])
def course_add(username):
    """
        User can create a course here
    """
    form = CourseCreateForm(request.form)
    courses=None
    if g.user.is_authenticated() and \
    g.user.username == username and \
    form.validate():
        # user can create the course
        course = Course()
        course.add_course(g.user.user_id,
                request.form['course_name'],
                request.form['course_ident'],
                request.form['course_section'],
                request.form['course_description'])
        g.user.update_courses()

    if not g.user.is_anonymous():
        courses = g.user.get_courses()

    return render_template('user/home.html', form=form, courses=courses)

@app.route('/<username>/<course>/')
def course_home(username, course):
    """
        Homepage for the course, displays recent assignments
    """
    return 'User %s, course %s' % (username, course)

@app.route('/<username>/<coursename>/delete')
@login_required
def course_delete(username, coursename):
    """
        Lets a user delete a course
    """
    form = CourseDeleteForm(request.form)
    if g.user.is_authenticated() and \
    g.user.username == username and \
    form.validate():
        # user owns and can delete the course
        course = Course()
        course.delete_course(g.user.user_id, coursename)
        g.user.update_courses()

    courses = None
    if not g.user.is_anonymous():
        courses = g.user.get_courses()

    return render_template('user/home.html', courses=courses)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'You logged out.'
