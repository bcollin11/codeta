"""
    CodeTA tests
    ============

    CodeTA unit tests

"""

import os
import unittest
import psycopg2
import logging
import zipfile

os.environ['CODETA_MODE'] = 'testing'

from codeta import app, db
from codeta.conf.testing import *
from codeta.models.database import Postgres
from codeta import logger
import grader.zip as zip

class CodetaTestCase(unittest.TestCase):

    # set up and tear down functions for tests
    def setUp(self):
        """ create tables in database for each test """
        self.app = app.test_client()
        app.config['WTF_CSRF_ENABLED'] = False
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

    def create_course(self, username, course_title, ident=None, section=None,
            description=None):

        if ident is None:
            ident = app.config['TEST_COURSE_IDENT']

        if section is None:
            section = app.config['TEST_COURSE_SECTION']

        if description is None:
            description = app.config['TEST_COURSE_DESCRIPTION']

        return self.app.post("/%s/new" % username,
                data={
                    'course_title': course_title,
                    'course_ident': ident,
                    'course_section': section,
                    'course_description': description
                }, follow_redirects=True)

    def delete_course(self, username, course_title, verification=None):

        if verification is None:
            verification = course_title

        return self.app.post("/%s/%s/delete" % (username, course_title),
            data={
                'course_title':  course_title,
                'verification': verification,
            }, follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username = username,
            password = password
            ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def create_file(self, name):
	try:
	    with open(name,'w') as file:
		file.write("test file")
	    return True
	except Exception as ex:
	    print ex
	    return False

    def create_zip(self,name):
        #creates a zip file with one directory and 2 files
        os.mkdir(name)
        self.create_file(os.path.join(name,"emptyfile1"))
        self.create_file(os.path.join(name,"emptyfile2"))
        newZip = zipfile.ZipFile(name + ".zip", "w")
        newZip.write(name)
        newZip.write(os.path.join(name,"emptyfile1"))
        newZip.write(os.path.join(name,"emptyfile2"))
        newZip.close()
        self.unlink_dir(name)

    def unlink_dir(self,folder):
	for file in os.listdir(os.path.join(os.getcwd(),folder)):
	    os.unlink(os.path.join(os.getcwd(),folder,file))
	os.rmdir(folder)

    # Unit tests
    def test_homepage(self):
        """
            Test the homepage for a user who has not logged in
        """
        rc = self.app.get('/')
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
        assert b'You are logged out.' in rc.data

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

        rc = self.create_course(
                app.config['TEST_USER'],
                app.config['TEST_COURSE_NAME'])
        assert b'Course: %s' % (app.config['TEST_COURSE_NAME']) in rc.data

        rc = self.create_course(
                app.config['TEST_USER'],
                app.config['TEST_COURSE_NAME'])
        assert b'This course already exists.' in rc.data

        rc = self.delete_course(
                app.config['TEST_USER'],
                app.config['TEST_COURSE_NAME'])
        assert b'Course: %s' % (app.config['TEST_COURSE_NAME']) not in rc.data

        # create course again for delete test
        rc = self.create_course(
                app.config['TEST_USER'],
                app.config['TEST_COURSE_NAME'])
        assert b'Course: %s' % (app.config['TEST_COURSE_NAME']) in rc.data

        # make sure only the owner of the account can create a course
        rc = self.create_course('a_different_user', 'course_should_not_exist')
        assert b'You can not create a course here.' in rc.data

        # make sure only owner can delete a course
        self.logout()
        self.register('test_user2', app.config['TEST_PW'])
        rc = self.login('test_user2', app.config['TEST_PW'])
        assert b'Logout' in rc.data

        rc = self.delete_course(
                app.config['TEST_USER'],
                app.config['TEST_COURSE_NAME'])
        assert b'You can not delete a course you do not own.' in rc.data

        self.logout()
        rc = self.delete_course(
                app.config['TEST_USER'],
                app.config['TEST_COURSE_NAME'])
        assert b'Login to Code TA' in rc.data

    def test_logout_redirect(self):
        """ test logging out without being logged in """
        rc = self.app.get('/')
        assert b'Logout' not in rc.data

        rc = self.logout()
        assert b'Login' in rc.data

    def test_errors(self):
        """ test 404 error page """
        rc = self.app.get('/this/should/not/exist/ever/', follow_redirects=True)
        assert b'404 error :(' in rc.data

    def test_setting_name(self):
        """
            Make sure our user can change their first and last name
        """
        self.register(app.config['TEST_USER'], app.config['TEST_PW'])
        rc = self.login(app.config['TEST_USER'], app.config['TEST_PW'])
        assert b'Logout' in rc.data

        rc = self.app.post('/%s/settings/name' % app.config['TEST_USER'],
            data={'fname': 'changedfname', 'lname': 'changedlname'},
            follow_redirects=True)
        assert b'changedfname' in rc.data
        assert b'changedlname' in rc.data

        rc = self.app.post('/%s/settings/name' % app.config['TEST_USER'],
            data={'fname': 'anotherfnamechange', 'lname': ''},
            follow_redirects=True)
        assert b'anotherfnamechange' in rc.data
        assert b'changedlname' in rc.data

        rc = self.app.post('/%s/settings/name' % app.config['TEST_USER'],
            data={'fname': '', 'lname': 'anotherlnamechange'},
            follow_redirects=True)
        logger.debug(rc.data)
        assert b'anotherfnamechange' in rc.data
        assert b'anotherlnamechange' in rc.data

    def test_setting_email(self):
        """
            Make sure we can change our email
        """
        self.register(app.config['TEST_USER'], app.config['TEST_PW'])
        rc = self.login(app.config['TEST_USER'], app.config['TEST_PW'])
        assert b'Logout' in rc.data

        rc = self.app.post('/%s/settings/email' % app.config['TEST_USER'],
            data={'email': 'changed@changed.com', 'confirm': 'changed@changed.com'},
            follow_redirects=True)

        assert b'changed@changed.com' in rc.data

        rc = self.app.post('/%s/settings/email' % app.config['TEST_USER'],
            data={'email': 'changed@changed.com', 'confirm': 'notthesame@changed.com'},
            follow_redirects=True)

        assert b'must match' in rc.data

        rc = self.app.post('/%s/settings/email' % app.config['TEST_USER'],
            data={'email': 'notvalidcom', 'confirm': 'notthesame@changed.com'},
            follow_redirects=True)
        assert b'must enter a valid email' in rc.data

    def test_setting_password(self):
        """
            Test changing password
        """
        self.register(app.config['TEST_USER'], app.config['TEST_PW'])
        rc = self.login(app.config['TEST_USER'], app.config['TEST_PW'])
        assert b'Logout' in rc.data

        rc = self.app.post('/%s/settings/password' % app.config['TEST_USER'],
            data={'password': 'changed_password', 'confirm': 'changed_password'},
            follow_redirects=True)

        self.logout()
        rc = self.login(app.config['TEST_USER'], 'changed_password')
        assert b'Logout' in rc.data

    def test_invalid_zip(self):
        """
	    Make sure an exception is raised when attempting to extract a non-zip file
	"""
        self.create_file("empty1")
	self.assertIsNone(zip.extract("empty1",os.getcwd()))
        os.unlink("empty1")

    def test_zip_extract(self):
	"""
	    Ensure zip files are extracted and in the right place
	"""
        testname = "testZip"
        self.create_zip(testname)
        zip.extract(testname+".zip",os.getcwd())
        folders = os.listdir(os.getcwd())
        assert testname in folders
        files = os.listdir(os.path.join(os.getcwd(),testname))
        assert "emptyfile1" in files
        assert "emptyfile2" in files
        self.unlink_dir(testname)
        os.unlink(testname+".zip")

    def test_zip_overwrite(self):
	"""
	    Ensure that extracted files can overwrite other files without error
	"""
        testname = "testZip"
        self.create_zip(testname)
        zip.extract(testname+".zip",os.getcwd())
        zip.extract(testname+".zip",os.getcwd())
        lines = os.listdir(os.path.join(os.getcwd(),testname))
        self.assertEqual(len(lines),2)
        self.unlink_dir(testname)
        os.unlink(testname+".zip")

if __name__ == '__main__':
    unittest.main()
