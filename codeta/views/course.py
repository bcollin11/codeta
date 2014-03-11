"""
    Views that handle course functionality.
    Course homepage, add assignments,
    course settings, etc.
"""
from flask import request

from codeta import app

@app.route('/<username>/<course>/')
def course_home(username, course):
    """
        Homepage for the course, displays recent assignments
    """
    return 'User %s, course %s' % (username, course)
