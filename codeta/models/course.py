from codeta import app, logger
from codeta.util.helpers import Callable

class Course(object):
    """
        A model for a course listed on CodeTA

        Let's users CRUD courses and add themselves
        to courses
    """

    def __init__(self):
        """
            Initialize a new course.
        """

    def add_course(self, user_id, title, ident, section, description):
        """ Add a new course that the user is teaching """

        sql = ("""
            insert into Course
                (course_id, title, identifier, section, description)
            values
                (%s, %s, %s, %s, %s)
            returning
                course_id
            """
        )

        data = (
            int(user_id),
            title,
            ident,
            section,
            description,
        )

        # add the user as an owner of the course
        course_id = app.db.exec_query(sql, data, 'commit', 'returning')
        self.add_course_instructor(user_id, course_id)

    def add_course_instructor(self, user_id, course_id):
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

    def get_courses(user_id):
        """
            static function to fetches a list of dictionaries, each tuple
            containing a course the user is an instructor in.

            Returns the list on success, None on error
        """

        sql = ("""
            select
                c.course_id, c.title, c.section
            from
                Course c, InstructorTeachesCourse i
            where
                c.course_id = i.course_id
            and
                i.user_id = (%s)
            """
        )

        data = (int(user_id), )

        courses = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        logger.debug('courses: %s' % courses)
        return courses

    get_courses = Callable(get_courses)

    def get_course_id(self, courses, course_title):
        """ Get the course ID for a given course_title and courses list """
        course_id = None
        for course in courses:
            if course.get('title') == course_title:
                course_id = course.get('course_id')
                break
        return course_id

    def delete_course(self, course_id):
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
