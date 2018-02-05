"""
postgres/psycopg2 wrapper
"""
import psycopg2
import os
from urllib import parse
from trip_test import app
from flask import g


def config(filename='database.ini', section='postgresql'):
    """ Loads database config """
    
    # Production
    if app.config['DEBUG'] == False:
        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])
        db_config = dict(database=url.path[1:],
                         user=url.username,
                         password=url.password,
                         host=url.hostname,
                         port=url.port
                        )
    # Development
    else:
        db_config = dict(host='localhost',
                         database='trip_test',
                         user='postgres',
                         password='default'
                        )
    return db_config


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
