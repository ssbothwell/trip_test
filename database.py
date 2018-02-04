"""
Sqlite database wrapper
"""
import sqlite3
from trip_test import app
from flask import g


def connect_db():
    """ connect to sqlite database """

    database = sqlite3.connect(app.config['DATABASE'])
    database.row_factory = sqlite3.Row
    return database


def get_db():
    """ returns the database if already connected
    else connects database and returns it """

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error) -> None:
    """ Close database connect """

    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db() -> None:
    """ Writes the schema file to the database """

    database = get_db()
    with app.open_resource('schema.sql', mode='r') as schema:
        database.cursor().executescript(schema.read())
    database.commit()


@app.cli.command('initdb')
def initdb_command() -> None:
    """ initialization function for use with
    the Flask CLI tool """

    init_db()
    print('Database initialized')
