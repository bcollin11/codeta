"""
    Contains forms for dealing with creating,
    deleting, modifying courses, etc
"""

from flask_wtf import Form
from wtforms import TextField, ValidationError, validators
from codeta.forms.validators import Exists

# TODO add custom validator
class CourseCreateForm(Form):
    """
        A form for creating a new course
    """

    def __init__(self, exists_data=None, *args, **kwargs):
        self.exists_data = exists_data
        super(CourseCreateForm, self).__init__(*args, **kwargs)

    course_title = TextField('Course title', [
        validators.Required(),
        validators.Length(max=100),
        Exists('title', 'This course already exists.')]
    )
    course_ident = TextField('Course ident', [validators.Required(), validators.Length(max=20)])
    course_section = TextField('Course section', [validators.Required()])
    course_description = TextField('Course description', [validators.Length(max=4096)])

class CourseDeleteForm(Form):
    """
        Form for deleting a course
    """

    course_title = TextField('Course title', [validators.Required(), validators.Length(max=100)])
    verification = TextField('Type the course title again',
            [validators.EqualTo('course_title', message='Confirmation must match.')])
