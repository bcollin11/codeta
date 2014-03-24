"""
    CodeTA
    ======

    A simple webapp to grade source code

"""
import os
import sys
import logging
import logging.config

from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash
from passlib.context import CryptContext
from flask.ext.login import (LoginManager, current_user, login_required,
        login_user, logout_user, UserMixin, AnonymousUserMixin, confirm_login,
        fresh_login_required)

from codeta.conf.logging import LOG_DICT
from codeta.models.security import Auth

app = Flask(__name__)

# Get configuration
app.config['CODETA_MODE'] = os.environ.get('CODETA_MODE')

if app.config['CODETA_MODE'] == 'production':
    app.config.from_pyfile('conf/production.py')

elif app.config['CODETA_MODE'] == 'development':
    app.config.from_pyfile('conf/development.py')

elif app.config['CODETA_MODE'] == 'testing':
    app.config.from_pyfile('conf/testing.py')

else:
    print '[ERROR] - Unrecognized mode: %s' % (app.config['CODETA_MODE'])
    print 'Please set the envvar `CODETA_MODE` = (production | development | testing)'
    sys.exit(1)

# Logging
logging.config.dictConfig(LOG_DICT)
logger = logging.getLogger(app.config['LOGGER'])

if app.config['DEBUG_LOGGING']:
    dbg_handler = logging.FileHandler(app.config['DEBUG_LOG_PATH'], 'a', None, True)
    f = logging.Formatter('%(asctime)s - [%(levelname)s] (%(filename)s:%(funcName)s:%(lineno)s) %(message)s')
    dbg_handler.setFormatter(f)
    dbg_handler.setLevel(logging.DEBUG)
    logger.addHandler(dbg_handler)

# Configure authentication
auth = Auth()

# Configure database
from codeta.models.database import Postgres
db = Postgres(auth, app)

# login_manager config
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_user(user_id)

# Import all our models and views
from codeta.views.user import *
from codeta.views.util import *
from codeta.views.main import *

from codeta.models.user import User

if __name__ == "__main__":
    app.run()
