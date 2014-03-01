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

    def add_course(self, user_id, name, ident, section, description):
        """ Add a new course that the user is teaching """

        sql = ("""
            insert into Course
                (instructor_id, name, identifier, section, description)
            values
                (%s, %s, %s, %s, %s)
            returning
                course_id
            """
        )

        data = (
            int(user_id),
            name,
            ident,
            int(section),
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
                (instructor_id, course_id)
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
            static function to fetches a list of tuples, each tuple
            containing a course the user is an instructor in.

            Returns the list on success, None on error
        """

        sql = ("""
            select
                c.course_id, c.name, c.section, c.instructor_id
            from
                Course c, InstructorTeachesCourse i
            where
                c.course_id = i.course_id
            and
                i.instructor_id = (%s)
            """
        )

        data = (int(user_id), )

        courses = app.db.exec_query(sql, data, 'fetchall')
        return courses

    get_courses = Callable(get_courses)

    def delete_course(self, user_id, coursename):
        """ Delete a course with the given name """
        course_id = [ x[2] for course in self.get_courses(user_id) if course[2] == coursename ]
        logger.debug("Course ID: %s" % course_id)

        sql = ("""
            delete from
                Course c, InstructorTeachesCourse i
            where
                c.name = (%s)
            and
                c.course_id = (%s)
            and
                c.course_id = i.course_id
            """
        )

        data = (
            coursename,
            int(course_id),
        )

        app.db.exec_query(sql, data, 'commit')
