from codeta import app, logger

class Assignment(object):
    """
        A model for a course assignment
    """
    def __init__(self, assignment_id=None, title=None,
                 description=None, due_date=None, points_possible=None,
                 course_id=None):

        self.assignment_id = assignment_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.points_possible = points_possible
        self.course_id = course_id

    def create(self):
        """
            Writes self to the database
        """

        sql = ("""
            insert into Assignment
                (title, description, due_date, points_possible, course_id)
            values
                (%s, %s, %s, %s, %s)
            returning
                assignment_id
            """
        )

        data = (
            self.title,
            self.description,
            self.due_date,
            self.points_possible,
            int(self.course_id),
        )

        logger.debug("Creating assignment: %s for course_id %s"
                    % (self.title, self.course_id))
        rc = app.db.exec_query(sql, data, 'commit', 'returning')
        if rc:
            logger.debug("Success")
            self.assignment_id = rc
        else:
            logger.debug("Fail")
            self.assignment_id = None

        return rc

    def delete(self):
        """
            Deletes self from the database
        """

        sql = ("""
            delete from
                Assignment
            where
                assignment_id = (%s)
            """
        )

        data = (
            int(self.assignment_id),
        )

        rc = app.db.exec_query(sql, data, 'commit')

        logger.debug("Deleting assignment: %s for course_id %s"
                    % (self.title, self.course_id))
        if rc:
            logger.debug("Success")
            self.assignment_id = None
        else:
            logger.debug("Failure")
        return rc

    def read(self):
        """
            Read the assignment from the database and set memvars
        """

        sql = ("""
            select
                *
            from
                Assignment
            where
                assignment_id = (%s)
            """
        )

        data = (
            int(self.assignment_id),
        )

        rc = app.db.exec_query(sql, data, 'fetchall', 'return_dict')

        logger.debug("Fetching assignment: %s " % (self.assignment_id))
        if rc:
            logger.debug("Success")
            a = a[0]
            self.title = a['title']
            self.description = a['description']
            self.due_date = a['due_date']
            self.points_possible = a['points_possible']
            self.course_id = a['course_id']
        else:
            logger.debug("Fail")
        return rc

    def update(self):
        """
            Update the assignment in the database
        """

        sql = ("""
            update Assignment set
                title = (%s),
                description = (%s),
                due_date = (%s),
                points_possible = (%s),
                course_id = (%s)
            where
                assignment_id = (%s)
            """
        )

        data = (
            self.title,
            self.description,
            self.due_date,
            self.points_possible,
            int(self.course_id),
            int(self.assignment_id),
        )

        logger.debug("Deleting assignment: %s for course_id %s"
                    % (self.title, self.course_id))
        rc = app.db.exec_query(sql, data, 'commit')

        if rc:
            logger.debug("Success")
        else:
            logger.debug("Fail")
        return rc

    @staticmethod
    def get_assignments(username, course_title):
        """
            Fetch a list of Assignment objects for a given course id
            returns an empty list if no assignments or error
        """

        sql = ("""
            select
                a.title, a.description, a.due_date, a.points_possible, c.course_id
            from
                Assignment a, Users u, InstructorTeachesCourse itc, Course c
            where
                c.title = (%s)
            and
                u.username = (%s)
            and
                u.user_id = itc.user_id
            and
                c.course_id = itc.course_id
            and
                a.course_id = itc.course_id
            """
        )

        data = (
            course_title,
            username,
        )

        logger.debug("Fetching assignments for user: %s, course_title: %s"
                    % (username, course_title))
        assignments = app.db.exec_query(sql, data, 'fetchall', 'return_dict')
        logger.debug(assignments)
        result = []
        if assignments:
            logger.debug("Success")
            for a in assignments:
                assignment = Assignment(
                    None, a['title'], a['description'],
                    a['due_date'], a['points_possible'], a['course_id'])

                result.append(assignment)
        else:
            logger.debug("Fail")
        return result

    @staticmethod
    def delete_assignment(assignment_id):
        """
            Delete an assignment with teh ID
        """
        sql = ("""
            delete from
                Assignment
            where
                assignment_id = (%s)
            """
        )

        data = (
            int(assignment_id),
        )

        rc = app.db.exec_query(sql, data, 'commit')

        logger.debug("Deleting assignment: %s for course_id %s"
                    % (self.title, self.course_id))
        if rc:
            logger.debug("Success")
            self.assignment_id = None
        else:
            logger.debug("Failure")
        return rc
