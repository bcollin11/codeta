"""
    Views that handle course functionality.
    Course homepage, add assignments,
    course settings, etc.
"""
from flask import (request, session, g, redirect, url_for,
        abort, render_template, flash)

from flask.ext.login import (current_user, login_required,
        login_user, logout_user, confirm_login,
        fresh_login_required)

from codeta import app, login_manager, logger
from codeta.models.course import Course
from codeta.models.user import User
from codeta.models.assignment import Assignment
from codeta.forms.course import CourseCreateForm, CourseDeleteForm

@app.route('/<username>/<course>/')
@login_required
def course_home(username, course):
    """
        Homepage for the course, displays recent assignments
    """
    assignments = Assignment.get_assignments(username, course)
    return render_template('course/home.html', course=course, username=username,
                            assignments=assignments)

@app.route('/<username>/new', methods=['GET', 'POST'])
@login_required
def course_create(username):
    """
        GET - show course creation form

        POST - create the course, add it to g.user.courses and
            add it to the database
    """
    form = None
    if g.user.is_authenticated():
        if g.user.username == username:
            form = CourseCreateForm(g.user.get_course_titles())
            if form.validate_on_submit():
                # user can create the course
                course = Course(
                        request.form['course_title'],
                        request.form['course_ident'],
                        request.form['course_section'],
                        request.form['course_description'],
                        g.user.user_id)
                course_id = course.create()
                if course_id:
                    course.add_instructor(g.user.user_id, course_id)
                    g.user.add_course(course)
                else:
                    flash('There was an error adding your class, please try again later.')
                return redirect(url_for('user_home', username=username))
            else:
                # there were errors on the form
                return render_template('user/new.html', form=form)
        else:
            # unauthorized user
            flash('You can not create a course here.')
            return redirect(url_for('user_home', username=g.user.username))
    else:
        # unauthenticated user
        return redirect(url_for('login'))

@app.route('/<username>/<course_title>/delete', methods=['GET', 'POST'])
@login_required
def course_delete(username, course_title):
    """
        GET - show course deletion form

        POST - delete the course from the database
    """
    form = None
    if g.user.is_authenticated():
        if g.user.username == username:
            form = CourseDeleteForm()
            if form.validate_on_submit():
                # user owns and can delete the course
                course_id = [ c.course_id for c in g.user.get_courses()
                        if c.title == course_title and c.instructor_id == g.user.user_id]
                Course.delete_course(int(course_id[0]))
                g.user.update_courses()
                flash('Course %s successfully deleted' % course_title)
                return redirect(url_for('user_home', username=username))
            else:
                # there were errors on the form
                return render_template('user/delete.html', form=form)
        else:
            # unauthorized user
            flash('You can not delete a course you do not own.')
            return redirect(url_for('user_home', username=g.user.username))
    else:
        # unauthenticated user
        return redirect(url_for('login'))
