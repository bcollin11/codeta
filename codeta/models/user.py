from flask.ext.login import UserMixin, AnonymousUserMixin

from codeta import app, auth, logger
from codeta.models.course import Course

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

    def create(self):
        """
            Register a user in the database
        """
        pw_hash = auth.hash_password(self.password)

        sql = ("""
            insert into Users
                (username, password, email, first_name, last_name)
            values
                (%s, %s, %s, %s, %s)
            returning
                user_id
            """)

        data = (
            self.username,
            pw_hash,
            self.email,
            self.fname,
            self.lname,
        )

        user_id = app.db.exec_query(sql, data, 'commit', 'returning')
        if user_id:
            self.user_id = user_id
            self.password = pw_hash
            logger.debug("Created new user_id: %s | username: %s" % (user_id, self.username))
        else:
            logger.debug("Failed to create username: %s" % (username))
        return user_id

    def read(self):
        """
            Update the User member variables with fresh data from the database
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
            int(self.user_id),
        )

        user = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        if user:
            user = user[0]
            self.user_id = int(user['user_id'])
            self.username = user['username']
            self.password = user['password']
            self.email = user['email']
            self.fname = user['first_name']
            self.lname = user['last_name']
        return user

    def update(self):
        """
            Update the user's data in the database from member variables
        """

        sql = ("""
            update Users set
                password = (%s),
                email = (%s),
                first_name = (%s),
                last_name = (%s)
            where
                user_id = (%s)
            """)

        data = (
            self.password,
            self.email,
            self.fname,
            self.lname,
            int(self.user_id),
        )
        commit = app.db.exec_query(sql, data, 'commit')
        if commit:
            logger.debug("Successfully updated user: %s" % (self.username))
        else:
            logger.debug("Failed to update user: %s" % (self.username))
        return commit

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def check_username(username):
        """
            Checks to see if a username already exists in the db.
            returns username if username is found, otherwise None
        """

        sql = ("""
            select
                username
            from
                Users
            where
                username = (%s)
            """)

        data = (
            username,
        )

        username = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        if username:
            return username[0].get('username')
        else:
            return None
