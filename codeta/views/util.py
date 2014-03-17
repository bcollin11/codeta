"""
    util.py contains utility views for server errors,
    redirects for login manager, etc
"""

from flask import request, session, g, redirect, url_for, \
        abort, render_template, flash

from flask.ext.login import (current_user, login_required,
        login_user, logout_user, confirm_login,
        fresh_login_required)

from codeta import app, db, login_manager, logger
from codeta.forms.login import LoginForm

@app.before_request
def before_request():
    """
        Set the current user =
        user in the request for
        flask-login
    """
    g.user = current_user

# Login Manager views
@login_manager.unauthorized_handler
def unauthorized():
    """
        return the login page when a user
        needs to be logged in to view a page
    """
    form = LoginForm(request.form)
    return render_template('user/login.html', form=form)

@login_manager.needs_refresh_handler
def refresh_login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = app.db.auth_user(
                request.form['username'],
                request.form['password'])
        if user:
            confirm_login(user)
            logger.info('User: %s - login auth success.' % (request.form['username']))
            return redirect(url_for('user_home', username=user.username))
        else:
            logger.info('User: %s - login auth failure.' % (request.form['username']))
            error = 'Invalid username or password.'
    return render_template('user/login.html', form=form, error=error)


@app.errorhandler(404)
def page_not_found(error):
    """ Return a 404 error page """
    return render_template('util/404.html'), 404

@app.errorhandler(403)
def page_forbidden(error):
    """ Return a 403 error page """
    return render_template('util/403.html'), 403
