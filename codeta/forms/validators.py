from wtforms import Form, ValidationError

class Exists(object):
    """
        Provides a validator that will query the database to make sure
        whatever doesn't exist
    """

    def __init__(self, key, message=None):
        """
            Checks to see if the field data is in the data
            dictionary. If so, errors with a message.

            data = dictionary to search through
            key = dict key to check against

        """
        self.key = key
        if not message:
            message = u'This already exists, sorry'
        self.message = message

    def __call__(self, form, field):
        for d in form.exists_data:
            if d.get(self.key) == field.data:
                raise ValidationError(self.message)
