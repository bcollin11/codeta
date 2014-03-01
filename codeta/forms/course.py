"""
    Contains forms for dealing with creating,
    deleting, modifying courses, etc
"""

from wtforms import Form, ValidationError, BooleanField, TextField, PasswordField, validators

class CourseCreateForm(Form):
    """
        A form for creating a new course
    """

    course_name = TextField('Course title', [validators.Required(), validators.Length(max=100)])
    course_ident = TextField('Course ident', [validators.Required(), validators.Length(max=20)])
    course_section = TextField('Course section', [validators.Required()])
    course_description = TextField('Course description', [validators.Length(max=4096)])
