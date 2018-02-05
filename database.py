"""
postgres/psycopg2 wrapper
"""
import psycopg2
from configparser import ConfigParser
from trip_test import app
from flask import g


def config(filename='database.ini', section='postgresql'):
    """ Loads database config """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return db


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        return conn

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get():
    """ returns the database if already connected
    else connects database and returns it """

    if not hasattr(g, 'postgres'):
        g.postgres = connect()
    return g.postgres


@app.teardown_appcontext
def close(error) -> None:
    """ Close database connect """

    if hasattr(g, 'postgres'):
        g.postgres.close()


def init() -> None:
    """ Writes the schema file to the database """

    database = get()
    cursor = database.cursor()
    with app.open_resource('schema.sql', mode='r') as schema:
        cursor.execute(schema.read())
    database.commit()


@app.cli.command('initdb')
def initdb_command() -> None:
    """ initialization function for use with
    the Flask CLI tool """

    init()
    print('Database initialized')
