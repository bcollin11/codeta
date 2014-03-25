"""
    Views that manage a user's account.

    Includes login/logout, join, user homepage, account settings,
    etc.

"""

from flask import request, session, g, redirect, url_for, \
        abort, render_template, flash

from flask.ext.login import (current_user, login_required,
        login_user, logout_user, confirm_login,
        fresh_login_required)

from codeta import app, login_manager, logger
from codeta.forms.registration import RegistrationForm
from codeta.forms.course import CourseCreateForm, CourseDeleteForm
from codeta.forms.user_settings import UserNameForm, UserEmailForm, UserPwForm
from codeta.forms.validators import Exists
from codeta.forms.login import LoginForm
from codeta.models.course import Course
from codeta.models.user import User

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
        User's homepage. Displays things about their courses
        and current assignments
    """
    u = User(None, username, None, None, None, None)
    courses = u.get_courses()

    return render_template('user/home.html', courses=courses, username=username)

@app.route('/<username>/new', methods=['GET', 'POST'])
@login_required
def course_add(username):
    """
        User can create a course here
    """
    form = None
    if g.user.is_authenticated():
        if g.user.username == username:
            form = CourseCreateForm(g.user.get_course_titles())
            if form.validate_on_submit():
                # user can create the course
                course = Course(request.form['course_title'],
                        request.form['course_ident'],
                        request.form['course_section'],
                        request.form['course_description'],
                        g.user.user_id)
                course_id = course.add_course()
                if course_id:
                    course.add_instructor(g.user.user_id, course_id)
                    g.user.add_course(course)
                else:
                    flash('There was an error adding your class, please try again later.')
                return redirect(url_for('user_home', username=username))
            else:
                # there were errors on the form
                return render_template('user/new.html', form=form)
        else:
            # unauthorized user
            flash('You can not create a course here.')
            return redirect(url_for('user_home', username=g.user.username))
    else:
        # unauthenticated user
        return redirect(url_for('login'))

@app.route('/<username>/<course_title>/delete', methods=['GET', 'POST'])
@login_required
def course_delete(username, course_title):
    """
        Lets a user delete a course
    """
    form = None
    if g.user.is_authenticated():
        if g.user.username == username:
            form = CourseDeleteForm()
            if form.validate_on_submit():
                # user owns and can delete the course
                course_id = [ c.course_id for c in g.user.get_courses()
                        if c.title == course_title and c.instructor_id == g.user.user_id]
                Course.delete_course(int(course_id[0]))
                g.user.update_courses()
                flash('Course %s successfully deleted' % course_title)
                return redirect(url_for('user_home', username=username))
            else:
                # there were errors on the form
                return render_template('user/delete.html', form=form)
        else:
            # unauthorized user
            flash('You can not delete a course you do not own.')
            return redirect(url_for('user_home', username=g.user.username))
    else:
        # unauthenticated user
        return redirect(url_for('login'))

@app.route('/<username>/settings')
@login_required
def user_settings(username):
    """
        User's settings page to change different settings
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
        Page for changing the user's name
    """
    if g.user.username == username:
        form = UserNameForm()
        if form.validate_on_submit():
            # change the name
            g.user.set_name(request.form['fname'], request.form['lname'])
            return redirect(url_for('user_settings', username=g.user.username))
        else:
            return render_template('user/settings/name.html', username=g.user.username, form=form)
    else:
        # unauthorized user
        return redirect(url_for('user_settings', username=g.user.username))

@app.route('/<username>/settings/email', methods=['GET', 'POST'])
@login_required
def user_setting_email(username):
    if g.user.username == username:
        form = UserEmailForm()
        if form.validate_on_submit():
            # change the name
            g.user.set_email(request.form['email'])
            return redirect(url_for('user_settings', username=g.user.username))
        else:
            return render_template('user/settings/email.html', username=g.user.username, form=form)
    else:
        # unauthorized user
        return redirect(url_for('user_settings', username=g.user.username))

@app.route('/<username>/settings/password', methods=['GET', 'POST'])
@fresh_login_required
def user_setting_password(username):
    if g.user.username == username:
        form = UserPwForm()
        if form.validate_on_submit():
            # change the name
            g.user.set_password(request.form['password'])
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
