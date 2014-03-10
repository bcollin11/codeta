from flask.ext.login import UserMixin, AnonymousUserMixin

from codeta import app, logger
from codeta.models.course import Course

class User(UserMixin):
    def __init__(self, user_id, username, password, email, active=True, courses=[]):
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

    def get_course_titles(self):
        """
            Gets a list of course titles the user is enrolled in
        """
        titles = []
        [ titles.append(c.title) for c in self.courses ]
        return titles

    def add_course(self, course):
        """
            Adds a course to the list of courses
        """
        self.courses.append(course)

    def update_courses(self):
        """ Get a new list of courses from the database """
        self.courses = Course.get_courses(self.username)
