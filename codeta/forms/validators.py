from wtforms import Form, ValidationError

class Exists(object):
    """
        Provides a validator that will query the database to make sure
        whatever doesn't exist.

        To use this you must set an instance variable
        called "form.exists_data" which is a list or tuple
        containing the items to compare the field data to
    """

    def __init__(self, exclude=True, message=None):
        """
            Checks to see if the field data is in the data
            dictionary. If so, errors with a message.

            exclude = If true, will raise ValidationError if the
            field.data is found in form.exists_data. If false,
            raise ValidationError if the field.data is NOT found
            in form.exists_data
        """
        self.exclude = exclude
        if not message:
            message = u'This already exists, sorry'
        self.message = message

    def __call__(self, form, field):
        if self.exclude:
            if field.data in form.exists_data:
                raise ValidationError(self.message)
        else:
            if field.data not in form.exists_data:
                raise ValidationError(self.message)
