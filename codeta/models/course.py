from codeta import app, logger
from codeta.util.helpers import Callable

class Course(object):
    def __init__(self, title, ident, section, description, instructor_id=None, course_id=None):
        """
            A model for a course listed on CodeTA

            title = title of course
            ident = identifier of course
            section = course section
            description = description of course
            instructor_id = id of the instructor that teaches the course
        """
        self.title = title
        self.ident = ident
        self.section = section
        self.description = description
        self.instructor_id = instructor_id
        self.course_id = course_id

    def add_course(self):
        """
            Adds this course to the database
            Returns the course_id of the added course on success
            returns None if the course already exists or error
        """

        sql = ("""
            select
                c.course_id
            from
                Course c, InstructorTeachesCourse i
            where
                c.course_id = i.course_id
            and
                i.user_id = (%s)
            and
                c.course_title = (%)
            """
        )

        data = (
            self.instructor_id,
            self.title,
        )

        title_exists = app.db.check_exists(sql, data)
        if not title_exists:
            sql = ("""
                insert into Course
                    (title, identifier, section, description)
                values
                    (%s, %s, %s, %s)
                returning
                    course_id
                """
            )

            data = (
                self.title,
                self.ident,
                self.section,
                self.description,
            )

            # add the user as an owner of the course
            course_id = app.db.exec_query(sql, data, 'commit', 'returning')
            self.course_id = course_id
            return course_id
        else:
            return None

    def add_instructor(self, user_id, course_id):
        """
            Adds a user to a course as an instructor
        """
        sql = ("""
            insert into InstructorTeachesCourse
                (user_id, course_id)
            values
                (%s, %s)
            """
        )

        data = (
            int(user_id),
            int(course_id),
        )

        app.db.exec_query(sql, data, 'commit')

    def add_student(self, user_id, course_id):
        """
            Adds a student to the course
        """

        sql = ("""
            insert into StudentEnrollsCourse
                (user_id, course_id)
            values
                (%s, %s)
            """
        )

        data = (
            int(user_id),
            int(course_id),
        )

        app.db.exec_query(sql, data, 'commit')

    def get_courses(username):
        """
            static function to fetches a list of dictionaries, each tuple
            containing a course the user is an instructor in.

            Returns the list on success, None on error
        """

        result = []
        # get the couress the user teaches
        sql = ("""
            select
                c.course_id, c.identifier, c.description, i.user_id, c.title, c.section
            from
                Course c, InstructorTeachesCourse i, Users u
            where
                c.course_id = i.course_id
            and
                i.user_id = u.user_id
            and
                u.username = (%s)
            """
        )

        data = (username, )
        courses = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        if courses:
            for c in courses:
                course = Course(c.get('title'),
                        c.get('identifer'),
                        c.get('section'),
                        c.get('description'),
                        c.get('user_id'),
                        c.get('course_id'))
                result.append(course)

        # get the courses the user is enrolled in
        sql = ("""
            select
                c.course_id, c.identifier, c.description, c.title, c.section
            from
                Course c, StudentEnrollsCourse s, Users u
            where
                c.course_id = s.course_id
            and
                s.user_id = u.user_id
            and
                u.username = (%s)
            """
        )

        data = (username, )
        courses = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        if courses:
            for c in courses:
                course = Course(c.get('title'),
                        c.get('identifer'),
                        c.get('section'),
                        c.get('description'),
                        c.get('user_id'),
                        c.get('course_id'))
                result.append(course)

        return result
    get_courses = Callable(get_courses)

    def delete_course(course_id):
        """ Delete a course with the given name """

        sql = ("""
            delete from
                Course c
            where
                c.course_id = (%s)
            """
        )

        data = (
            int(course_id),
        )

        app.db.exec_query(sql, data, 'commit')
    delete_course = Callable(delete_course)
