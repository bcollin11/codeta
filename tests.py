"""
    CodeTA tests
    ============

    CodeTA unit tests

"""

import os
import unittest
import psycopg2
import logging

os.environ['CODETA_MODE'] = 'testing'

from codeta import app, db
from codeta.conf.testing import *
from codeta.models.database import Postgres
from codeta import logger

class CodetaTestCase(unittest.TestCase):

    # set up and tear down functions for tests
    def setUp(self):
        """ create tables in database for each test """
        self.app = app.test_client()
        db.init_db()

    def tearDown(self):
        """ drop all the tables and close connection """
        with app.app_context():
            db = app.db.get_db()
            cur = db.cursor()
            with app.open_resource('sql/drop_tests.sql', mode='r') as f:
                cur.execute(f.read())
            db.commit()
            cur.close()
            db.close()

    # unit test helper functions
    def register(self, username, password, password2=None,
            email=None, email2=None, fname=None, lname=None):
        """ registers a test user """

        if password2 is None:
            password2 = password

        if email is None:
            email = "%s@codeta_test.com" % (username)

        if email2 is None:
            email2 = "%s@codeta_test.com" % (username)

        if fname is None:
            fname = username

        if lname is None:
            lname = username

        return self.app.post('/join', data={
            'username': username,
            'password': password,
            'confirm_password': password2,
            'email': email,
            'confirm_email': email2,
            'fname': fname,
            'lname': lname
            }, follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username = username,
            password = password
            ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # Unit tests
    def test_homepage(self):
        """
            Test the homepage for a user who has not logged in
        """
        rc = self.app.get('/')
        assert b'Welcome to Code TA' in rc.data
        assert b'Logout' not in rc.data

    def test_register(self):
        """ Test registering for a new account """
        rc = self.register(
                app.config['TEST_USER'],
                app.config['TEST_PW'])
        assert b'Login to Code TA' in rc.data

        rc = self.register(
                app.config['TEST_USER'],
                app.config['TEST_PW'])
        assert b'Sorry, that username is already taken.' in rc.data

        rc = self.register('', 'derp')
        assert b'Field must be between 1 and 100 characters long.' in rc.data

        rc = self.register('derp', '')
        assert b'This field is required.' in rc.data

        rc = self.register('derp', 'pass', 'not same pass')
        assert b'Passwords must match.' in rc.data

        rc = self.register('derp', 'pass', 'pass', email='broken', email2='broken')
        assert b'You must enter a valid email address.' in rc.data

        rc = self.register('derp', 'pass', 'pass', email='broken@broken.com')
        assert b'Email addresses must match.' in rc.data

    def test_login_logout(self):
        """
            Test logging in and logging out
            and failed login error cases
        """
        self.register(
                app.config['TEST_USER'],
                app.config['TEST_PW'])

        rc = self.login(
                app.config['TEST_USER'],
                app.config['TEST_PW'])
        assert b'Logout' in rc.data

        rc = self.logout()
        assert b'You logged out.' in rc.data

        rc = self.login(
                app.config['TEST_USER'],
                'wrong password')
        assert b'Invalid username or password.' in rc.data

        rc = self.login(
                'user_doesnt_exist',
                'wrong password')
        assert b'Invalid username or password.' in rc.data

    def test_create_delete_course(self):
        """
            Test creating and deleting courses for a user
        """
        self.register(
                app.config['TEST_USER'],
                app.config['TEST_PW'])

        rc = self.login(
                app.config['TEST_USER'],
                app.config['TEST_PW'])
        assert b'Logout' in rc.data

        rc = self.app.post("/%s/add" % (app.config['TEST_USER']),
                data={
                    'course_name':         app.config['TEST_COURSE_NAME'],
                    'course_ident':        app.config['TEST_COURES_IDENT'],
                    'course_section':      app.config['TEST_COURSE_SECTION'],
                    'course_description':  app.config['TEST_COURSE_DESCRIPTION']
                })
        logger.debug(rc.data)
        assert b'Course: %s' % (app.config['TEST_COURSE_NAME']) in rc.data

        rc = self.app.post("/%s/delete" % (app.config['TEST_USER']),
                data={
                    'course_name':  app.config['TEST_COURSE_NAME'],
                    'verification': app.config['TEST_COURSE_NAME'],
                })
        assert b'Course: %s' % (app.config['TEST_COURSE_NAME']) not in rc.data

    def test_logout_redirect(self):
        """ test logging out without being logged in """
        rc = self.logout()
        assert b'You logged out.' in rc.data

    def test_errors(self):
        """ test 404 error page """
        rc = self.app.get('/this/should/not/exist/ever/', follow_redirects=True)
        assert b'404 error :(' in rc.data


if __name__ == '__main__':
    unittest.main()
