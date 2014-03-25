from flask.ext.login import UserMixin, AnonymousUserMixin

from codeta import app, auth, logger
from codeta.models.course import Course
from codeta.util.helpers import Callable

class User(UserMixin):
    def __init__(self, user_id, username, password, email, fname, lname, active=True, courses=[]):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.fname = fname
        self.lname = lname
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

    def set_name(self, fname=None, lname=None):
        """ Update the user's name in the db """
        if not (fname or lname):
            # No update to fname or lname
            return

        if fname and lname:
            sql = ("""
                update Users set
                   first_name = (%s),
                   last_name = (%s)
                where
                    user_id = (%s)
                """)

            data = (
                fname,
                lname,
                int(self.user_id),
            )
            self.fname = fname
            self.lname = lname
        elif fname:
            sql = ("""
                update Users set
                   first_name = (%s)
                where
                    user_id = (%s)
                """)

            data = (
                fname,
                int(self.user_id),
            )
            self.fname = fname
        elif lname:
            sql = ("""
                update Users set
                   last_name = (%s)
                where
                    user_id = (%s)
                """)

            data = (
                lname,
                int(self.user_id),
            )
            self.lname = lname
        app.db.exec_query(sql, data, 'commit')

    def set_email(self, email):
        """
            Updates the user's email in the database
        """
        sql = ("""
            update Users set
                email = (%s)
            where
                user_id = (%s)
            """)

        data = (
            email,
            int(self.user_id),
        )
        app.db.exec_query(sql, data, 'commit')
        self.email = email

    def set_password(self, password):
        """
            Updates a user's password in the database
        """
        pw_hash = auth.hash_password(password)

        sql = ("""
            update Users set
                password = (%s)
            where
                user_id = (%s)
            """)

        data = (
            pw_hash,
            int(self.user_id),
        )
        app.db.exec_query(sql, data, 'commit')
        self.password = pw_hash

    def auth_user(username, password):
        """
            Authenticates a user and returns a User object
            if the correct credentials were provided
            otherwise, return None
        """
        logger.debug("User: %s - Pass: %s - auth attempt. " % (username, password))

        sql = ("""
            select
                *
            from
                Users
            where
                username = (%s)
            """)

        data = (
            username,
        )

        user = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        if user:
            user = user[0]
            if(auth.check_password(password, user['password'])):
                user = User(
                    int(user['user_id']),
                    user['username'],
                    user['password'],
                    user['email'],
                    user['first_name'],
                    user['last_name'])
                logger.debug("User: %s - auth success." % (username))
            else:
                user = None
                logger.debug("User: %s - auth failure." % (username))
        return user
    auth_user = Callable(auth_user)

    def get_user(user_id):
        """
            Creates a new User object from the database
            returns a User object if found, otherwise None
        """
        sql = ("""
            select
                *
            from
                Users
            where
                user_id = (%s)
            """)

        data = (
            int(user_id),
        )

        user = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        if user:
            user = user[0]
            user = User(
                    int(user['user_id']),
                    user['username'],
                    user['password'],
                    user['email'],
                    user['first_name'],
                    user['last_name'])
        return user
    get_user = Callable(get_user)
