"""
    Forms for modifying user settings
"""

from flask_wtf import Form
from wtforms import TextField, ValidationError, validators

class UserNameForm(Form):


    fname = TextField('First name', [
        validators.Regexp("^[a-zA-Z]*$", message="You may only user letters A-Z"),
        validators.Optional()])

    lname = TextField('Last name', [
        validators.Regexp("^[a-zA-Z]*$", message="You may only user letters A-Z"),
        validators.Optional()])


class UserEmailForm(Form):

    email = TextField('Email Address', [
        validators.Length(min=1, max=100),
        validators.Required(),
        validators.EqualTo('confirm', message='Email addresses must match.'),
        validators.Email(message='You must enter a valid email address.')
        ])
    confirm = TextField('Repeat email address', [validators.Length(min=3, max=100)])
