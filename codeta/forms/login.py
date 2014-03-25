from flask_wtf import Form
from wtforms import ValidationError, BooleanField, TextField, PasswordField, validators

from codeta import app, db


class LoginForm(Form):
    """
        Provides the login form for the login page

        Requires valid username and password
    """

    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
