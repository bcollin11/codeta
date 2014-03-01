from flask.ext.login import UserMixin, AnonymousUserMixin

from codeta import app, logger
from codeta.models.course import Course

class User(UserMixin):
    def __init__(self, user_id, username, password, email, active=True):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.active = active
        self.update_courses()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.user_id)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_courses(self):
        return self.courses

    def update_courses(self):
        """ update the user's list of courses"""
        self.courses = Course.get_courses(self.user_id)
