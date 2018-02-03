import os
import sqlite3
import re
from flask import (Flask, request, session, g, jsonify,
                   abort, url_for, redirect, render_template)
from flask_jwt_extended import (JWTManager, jwt_required,
                                create_access_token, 
                                get_jwt_identity)

### Configuration

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

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


### Database management

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


### Controllers

@app.route('/index', methods=['GET'])
def index():
    db = get_db()
    query = db.execute('SELECT memberID, name, email, phone FROM members order by memberID desc')
    entries = query.fetchall() 
    return render_template('index.html', entries=entries)


@app.route('/', methods=['GET'])
@jwt_required
def get_entry():
    # Validate access rights
    username, access_rights = get_jwt_identity()
    if access_rights == 0:
        return jsonify({"msg": "Access Denied"}, 200)

    # Validate request
    if not valid_json(request):
        return jsonify({"msg": "Missing JSON in request"}, 400)

    # Query database
    db = get_db()
    memberID = request.json['memberID']

    query = db.execute('SELECT * FROM members where memberID=?', [memberID]).fetchall()
    entries = [ { 'memberID': row['memberID'],
                  'name': row['name'],
                  'phone': row['phone'],
                  'email': row['email']
                }
                for row in query]
    return jsonify(entries, 200)


@app.route('/', methods=['PUT'])
@jwt_required
def add_entry():
    # Validate access rights
    username, access_rights = get_jwt_identity()
    if access_rights <= 1:
        return jsonify({"msg": "Access Denied"}, 200)
    
    # Validate request
    if not valid_json(request):
        return jsonify({"msg": "Missing JSON in request"}), 400
    if not (valid_email(request.json['email']) or 
            valid_phone(request.json['phone'])):
        return jsonify({"msg": "Please enter valid email and phone numbers"}), 400

    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
          
    # Query Database
    db = get_db()
    existing_user = db.execute('SELECT name FROM members WHERE name=?',
                               [name]).fetchall()
    # Update row
    if existing_user:
        db.execute('UPDATE members SET phone=?,email=? WHERE name=?', 
                   [phone, email, name])
    # Create row
    else:
        db.execute('INSERT INTO members (name, email, phone) VALUES (?, ?, ?)',
                     [name, email, phone])
    db.commit()
    return jsonify({"msg": "success"}), 201


@app.route('/', methods=['DELETE'])
@jwt_required
def delete_entry():
    # Validate access rights
    username, access_rights = get_jwt_identity()
    if access_rights <= 2:
        return jsonify({"msg": "Access Denied"}, 200)

    # Validate request
    if not valid_json(request):
        return jsonify({"msg": "Missing JSON in request"}), 400
    db = get_db()
    memberID = request.json['memberID']

    # Check for entry
    existing_user = db.execute('SELECT name FROM members WHERE memberID=?',
                               [memberID]).fetchall()
    if existing_user:
        db.execute('DELETE FROM members WHERE memberID=?', [memberID])
        db.commit()
        return jsonify({"msg": "success"}), 200
    return jsonify({"msg": "no such entry"}), 404


@app.route('/login', methods=['POST'])
def login():
    """ Accept login info and return JWT token """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    # Get user access rights from database
    db = get_db()
    query = db.execute('SELECT * FROM users where username=?', [username]).fetchall()
    if query:
        db_password = query[0]['password']
        # Wrong password
        if password != db_password:
            return jsonify({"msg": "Bad username or password"}), 401
        # Success
        else:
            access_token = create_access_token(identity=[username, query[0]['access_rights']])
            return jsonify(access_token=access_token), 200
    # No such username
    else:
        return jsonify({"msg": "Bad username or password"}), 401



### Validation Helper functions

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

    if ((request.method == 'DELETE' or
        request.method == 'GET') and 
        not 'memberID' in request.json):
        return False

    if (request.method == 'PUT' and 
        (not 'name' in request.json or 
         not 'email' in request.json or 
         not 'phone' in request.json)):
        return False
    return True
