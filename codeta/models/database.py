from flask import g

import psycopg2
import psycopg2.extras

from codeta.models.user import User
from codeta import logger

class Postgres(object):
    """
        Provides functions to connect to the database,
        and to query various things from the db
    """

    def __init__(self, auth, app=None):
        """
            Initialize and add to our flask app
            as app.db

            auth = security model for checking passwords
            app = flask app to bind to

        """

        self.auth = auth
        app.db = self
        self.app = app


    def close_db(self):
        """
            Closes the database at the end of the request
        """
        if hasattr(g, 'pgsql_db'):
            g.pgsql_db.close()

    def connect_db(self):
        """
            Connect to the database in the app.config
            returns a connection object on success
        """
        conn = psycopg2.connect(
                dbname = self.app.config['DATABASE'],
                user = self.app.config['DB_USER'],
                password = self.app.config['DB_PASSWORD']
        )

        return conn

    def check_exists(self, sql, data, *args, **kwargs):
        """
            Wrapper to check if data exists in the database.

            Only contains error handling for sql SELECT.
            If you need another query, use exec_query()
        """

        with self.app.app_context():
            db = self.get_db()
            cur = db.cursor()
            result = None

            try:
                cur.execute(sql, data)
                result = cur.fetchone()

            except Exception, e:
                result = None

            return result

    def get_db(self):
        """
            Gets the current database cursor or creates one if not found
            the g object is a thread-safe storage object for database
            connections
        """
        if not hasattr(g, "pgsql_db"):
            g.pgsql_db = self.connect_db()
        return g.pgsql_db

    def get_username(self, username):
        """
            Checks to see if a username already exists in the db.
            returns True if username is found, otherwise False
        """

        user = None
        with self.app.app_context():
            if username:
                db = self.get_db()
                cur = db.cursor()
                cur.execute("SELECT username FROM Users WHERE username = (%s)", (username, ))
                user = cur.fetchone()
                cur.close()
        return user

    def init_db(self):
        """
            create the database tables in teh schema if not found
        """
        with self.app.app_context():
            db = self.get_db()
            with self.app.open_resource('sql/init_codeta.sql', mode='r') as f:
                db.cursor().execute(f.read())
            db.commit()

    def register_user(self, username, password, email, fname, lname):
        """
            Register a user in the database
        """
        with self.app.app_context():
            db = self.get_db()

            pw_hash = self.auth.hash_password(password)

            sql = "INSERT INTO Users (username, password, email, first_name, last_name) \
                VALUES (%s, %s, %s, %s, %s)"

            data = (
                username,
                pw_hash,
                email,
                fname,
                lname,
            )

            db.cursor().execute(sql, data)
            db.commit()

    def exec_query(self, sql, data, *args, **kwargs):
        """
            Executes a database query and returns the result
            sql = a tuple containing the query as a string
            data = a tuple of data values to insert into the sql
            commit = Does this sql query need an explicit commit? Default false

            args = [
                fetchall - returns the result of a fetchall against the cursor
                fetchone - returns the result of a fetchone against the cursor
                commit - if commit, then the query requires a commit
                returning - returns data from the row inserted
                return_dict - return a list of dictionaries with the column name as the key
                and the value as the dictionary
            ]

        """

        with self.app.app_context():
            db = self.get_db()
            cur = db.cursor()
            result = None

            try:
                cur.execute(sql, data)

                if 'fetchall' in args:
                    result = cur.fetchall()

                if 'fetchone' in args:
                    result = cur.fetchone()

                if 'returning' in args:
                    result = cur.fetchone()[0]

                if 'return_dict' in args:
                    colnames = [desc[0] for desc in cur.description]
                    result_dicts = [ dict(zip(colnames, row)) for row in result ]
                    result = result_dicts

                if 'commit' in args:
                    db.commit()

            except psycopg2.IntegrityError, e:
                logger.warn('db_query failed: %s' % (e[0]))
                logger.debug('db_query == %s data == %s' % (sql, data))
                db.rollback()
                result = None
            except Exception, e:
                logger.warn('db_query failed: %s' % (e[0]))
                logger.debug('db_query == %s data == %s' % (sql, data))
                result = None

            return result
