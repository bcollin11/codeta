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
