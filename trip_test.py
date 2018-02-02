import os
import sqlite3
import re
from flask import (Flask, request, session, g, jsonify,
                   abort, render_template)


# Create application instance and load config
app = Flask(__name__)
app.config.from_object(__name__)

# Default config
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'trip_test.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('TRIP_SETTINGS', silent=True)


def connect_db():
    """ connect to sqlite database """
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """ returns the database if already connected
    else connects database and returns it """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """ Close database connect """
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    """ Writes the schema file to the database """
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """ initialization function for use with
    the Flask CLI tool """
    init_db()
    print('Database initialized')


@app.route('/', methods=['GET'])
def index():
    db = get_db()
    query = db.execute('SELECT name, email, phone FROM members order by memberID desc')
    entries = query.fetchall() 
    return render_template('index.html', entries=entries)


@app.route('/', methods=['PUT'])
def add_entry():
    if not valid_json(request):
        return abort(400)
    if not (valid_email(request.json['email']) or 
            valid_phone(request.json['phone'])):
        return abort(400)

    member = { 'name': request.json['name'],
               'email': request.json['email'],
               'phone': request.json['phone']
             }

    db = get_db()

    # Check if the user already has an entry
    existing_user = db.execute('SELECT name FROM members WHERE name=?',
                               [member['name']]).fetchall()

    if existing_user:
        db.execute('UPDATE members SET phone=?,email=? WHERE name=?', 
                   [member['phone'], member['email'], member['name']])
    else:
        db.execute('INSERT INTO members (name, email, phone) VALUES (?, ?, ?)',
                     [member['name'], member['email'], member['phone']])
    db.commit()
    return jsonify({'member': member}, 201)


## Helper functions

def valid_phone(phone_number: str) -> bool:
    pattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$', re.VERBOSE)
    return pattern.match(phone_number) is not None


def valid_email(email: str) -> bool:
    pattern = re.compile(r'[^@]+@[^@]+\.[^@]+', re.VERBOSE)
    return pattern.match(email) is not None


def valid_json(request) -> bool:
    """ ensure json requests contain correct fields """
    if not request.json:
        return False
    if (not 'name' in request.json or 
        not 'email' in request.json or 
        not 'phone' in request.json):
        return False
    return True
