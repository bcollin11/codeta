from flask import (request, session, g, redirect, url_for,
        abort, render_template, flash)

from flask.ext.login import (current_user, login_required,
        login_user, logout_user, confirm_login,
        fresh_login_required)

from codeta import app, login_manager, logger
from codeta.models.course import Course
from codeta.models.user import User
from codeta.models.assignment import Assignment
from codeta.views.course import course_home
from codeta.forms.assignment import AssignmentCreateForm, AssignmentDeleteForm

@app.route('/<username>/<course>/new', methods=['GET', 'POST'])
@login_required
def assignment_create(username, course):
    """
        GET - Show the assignment creation form

        POST - Validate the form and create the assignment
    """

    form = None
    if g.user.is_authenticated():
        if g.user.username == username:
            asn_titles = [ a.title for a in
                    Assignment.get_assignments(username, course) ]
            course_id = [ c.course_id for c in g.user.get_courses()
                    if c.title == course and c.instructor_id == g.user.user_id]
            form = AssignmentCreateForm(asn_titles)
            if course_id[0] and form.validate_on_submit():
                assignment = Assignment(
                        None,
                        request.form['assignment'],
                        request.form['description'],
                        request.form['due_date'],
                        request.form['points'],
                        course_id[0])
                rc = assignment.create()
                return redirect(url_for('course_home', username=username,
                                course=course))
            else:
                return render_template('assignment/create.html', course=course,
                                        form=form)
        else:
            # unauthorized user
            flash('You can not create an assignment here.')
            return redirect(url_for('course_home', username=username,
                            course=course))
    else:
        return redirect(url_for('login'))

@app.route('/<username>/<course>/<assignment>/delete', methods=['GET', 'POST'])
@login_required
def assignment_delete(username, course, assignment):
    """
        GET - Show the assignment delete form

        POST - Validate the form and delete the assignment
    """

    form = None
    if g.user.is_authenticated():
        if g.user.username == username:
            asn_id = [ a.assignment_id for a in
                        Assignment.get_assignments(username, course)
                        if a.assignment_id == assignment]
            form = AssignmentDeleteForm()
            course_id = [ c.course_id for c in g.user.get_courses()
                    if c.title == course and c.instructor_id == g.user.user_id]
            if course_id[0] and form.validate_on_submit():
                rc = Assignment.delete_assignment()
                return redirect(url_for('course_home', username=username,
                                course=course))
            else:
                return render_template('assignment/delete.html', course=course,
                                        form=form, assignment=assignment)
        else:
            # unauthorized user
            flash('You can not delete that.')
            return redirect(url_for('course_home', username=username,
                            course=course))
    else:
        return redirect(url_for('login'))
