from flask_wtf import Form
from wtforms import (TextField, TextAreaField, IntegerField, DateTimeField,
    ValidationError, validators)
from codeta.forms.validators import Exists

class AssignmentCreateForm(Form):
    def __init__(self, exists_data=None, *args, **kwargs):
        self.exists_data = exists_data
        super(AssignmentCreateForm, self).__init__(*args, **kwargs)

    assignment = TextField(
            'Assignment Title', [
                validators.Required(),
                validators.Length(max=100),
                validators.Regexp('^\w*$', 0, "You can only use letters and underscores."),
                Exists(True, 'You already have an assignment called that.')
                ]
            )

    description = TextAreaField(
            'Instructions for the assignment', [
                validators.Required(),
                validators.Length(max=50000)
                ]
            )

    due_date = DateTimeField('Due date for the assignment')

    points = IntegerField(
            'Enter a point value for the assignment', [
                validators.Required(),
                validators.NumberRange(0, None, 'Please enter a positive integer')
                ]
            )

class AssignmentDeleteForm(Form):
    assignment = TextField(
            'Assignment Title', [
                validators.Required(),
                validators.Length(max=100),
                validators.Regexp('^\w*$', 0, "You can only use letters and underscores."),
                ]
            )

    confirm = TextField(
            'Type assignment title again to confirm deletion', [
                validators.EqualTo(assignment, 'Confirmation must match the title')
                ]
            )
