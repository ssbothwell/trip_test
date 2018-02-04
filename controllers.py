"""
Controllers
"""
import re
import sqlite3
from trip_test import app
from trip_test import database
from flask import (request, g, jsonify, render_template)
from flask_jwt_extended import (jwt_required,
                                create_access_token,
                                get_jwt_identity)


@app.route('/', methods=['GET'])
@jwt_required
def get_entry() -> request:
    """ Retrieve a member from the member table.
    Requires acess_rights >= 1 """

    # Validate access rights
    _, access_rights = get_jwt_identity()
    if access_rights == 0:
        return jsonify({"msg": "Access Denied"}), 403

    # Validate request
    if not valid_json(request):
        return jsonify({"msg": "Missing JSON in request"}), 400

    # Query database
    db = database.get()
    member_id = request.get_json()['memberID']

    query = db.execute('SELECT * FROM members where memberID=?', [member_id]).fetchall()
    entries = [{'memberID': row['memberID'],
                'name': row['name'],
                'phone': row['phone'],
                'email': row['email']
               } for row in query]
    if entries:
        return jsonify(entries[0]), 200
    else:
        return jsonify({'msg': 'No Such User'}), 400


@app.route('/', methods=['PUT'])
@jwt_required
def add_entry() -> request:
    """ Add or update a member in the member table.
    Requires acess_rights == 2 """

    # Validate access rights
    _, access_rights = get_jwt_identity()
    if access_rights <= 1:
        return jsonify({"msg": "Access Denied"}), 200

    # Validate request
    if not valid_json(request):
        return jsonify({"msg": "Missing JSON in request"}), 400
    if not (valid_email(request.get_json()['email']) or
            valid_phone(request.get_json()['phone'])):
        return jsonify({"msg": "Please enter valid email and phone numbers"}), 400

    name = request.get_json()['name']
    email = request.get_json()['email']
    phone = request.get_json()['phone']

    # Query Database
    # Based on my research, the `sqlite3` module does not
    # return errors from the sqlite database. This is an
    # issue for us detecting insertions with duplicate `name`
    # fields.
    # As a work-around I am doing a second query to check
    # for existing records with the desired `name` field.

    db = database.get()
    user = db.execute('SELECT name FROM members WHERE name=?',
                            [name]).fetchone()
    # Name field already exists
    if user:
        return jsonify({"msg": "Name Already Exists"}), 409
    # Name field doesn't exist so create a row
    else:
        db.execute('INSERT INTO members (name, email, phone) \
                         VALUES (?, ?, ?)', [name, email, phone])
    db.commit()
    return jsonify({"msg": "Success"}), 201


@app.route('/', methods=['DELETE'])
@jwt_required
def delete_entry() -> request:
    """ Removes a user with given memberID from
    the member table. Requires acess_rights == 3 """

    # Validate access rights
    _, access_rights = get_jwt_identity()
    if access_rights <= 2:
        return jsonify({"msg": "Access Denied"}), 200

    # Validate request
    if not valid_json(request):
        return jsonify({"msg": "Missing JSON in request"}), 400
    db = database.get()
    member_id = request.get_json()['memberID']

    # Check for entry
    user = db.execute('SELECT name FROM members WHERE memberID=?',
                            [member_id]).fetchall()
    if user:
        db.execute('DELETE FROM members WHERE memberID=?',
                         [member_id])
        db.commit()
        return jsonify({"msg": "success"}), 200
    return jsonify({"msg": "No Such Entry"}), 404


@app.route('/login', methods=['POST'])
def login() -> request:
    """ Accept login info and return JWT token """

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.get_json().get('username', None)
    password = request.get_json().get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    # Get user access rights from database
    db = database.get()
    query = db.execute('SELECT * FROM users where username=?',
                             [username]).fetchall()
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
    """ Validates a phone number using a regex pattern """
    pattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$', re.VERBOSE)
    return pattern.match(phone_number) is not None


def valid_email(email: str) -> bool:
    """ Validates a email using a regex pattern """
    pattern = re.compile(r'[^@]+@[^@]+\.[^@]+', re.VERBOSE)
    return pattern.match(email) is not None


def valid_json(req: request) -> bool:
    """ ensure json requests contain correct fields """
    if not req.json:
        return False

    if ((req.method == 'DELETE' or
         req.method == 'GET') and
            not 'memberID' in req.json):
        return False

    if (req.method == 'PUT' and
           (not 'name' in req.json or
            not 'email' in req.json or
            not 'phone' in req.json)):
        return False
    return True