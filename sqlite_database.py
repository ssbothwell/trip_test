"""
Sqlite database wrapper
"""
import sqlite3
from trip_test import app
from flask import g


def connect():
    """ connect to sqlite database """

    database = sqlite3.connect(app.config['DATABASE'])
    database.row_factory = sqlite3.Row
    return database


def get():
    """ returns the database if already connected
    else connects database and returns it """

    if not hasattr(g, 'sqlite'):
        g.sqlite = connect()
    return g.sqlite


@app.teardown_appcontext
def close(error) -> None:
    """ Close database connect """

    if hasattr(g, 'sqlite'):
        g.sqlite.close()


def init() -> None:
    """ Writes the schema file to the database """

    database = get()
    with app.open_resource('schema.sql', mode='r') as schema:
        database.cursor().executescript(schema.read())
    database.commit()


@app.cli.command('initdb')
def initdb_command() -> None:
    """ initialization function for use with
    the Flask CLI tool """

    init()
    print('Database initialized')
