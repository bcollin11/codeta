"""
    Default config options for automated tests
"""

# Core
DEBUG = True
TESTING = True

# Database
DATABASE = 'codeta_test'
SECRET_KEY = 'test key'
DB_USER = 'pguser'
DB_PASSWORD = 'default'

# User
TEST_USER = 'test_instructor'
TEST_PW = 'test_password'

# Course
TEST_COURSE_NAME = 'test_course'
TEST_COURSE_IDENT = 'CSET'
TEST_COURSE_SECTION = '001'
TEST_COURSE_DESCRIPTION = 'Test course description text'

# Logging
LOGGER = 'testing'
DEBUG_LOGGING = True
DEBUG_LOG_PATH = '/tmp/codeta-debug.log'
