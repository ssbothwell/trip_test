"""
Controllers
"""
from application import app
from application import database
from application import validators
from flask import request, jsonify
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
    if not validators.json(request):
        return jsonify({"msg": "Missing JSON In Request"}), 400

    member_id = request.get_json()['memberID']

    # Connect to database
    db_connection = database.get()

    # Get a cursor
    cursor = db_connection.cursor()

    # Query table for member
    statement = 'SELECT * FROM members WHERE memberID=%s'
    cursor.execute(statement, (member_id,))
    member = cursor.fetchone()

    if member:
        member_dict = { 'memberID': member[0],
                        'name': member[1],
                        'email': member[2],
                        'phone': member[3]
                      }
        return jsonify(member_dict), 200
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
    if not validators.json(request):
        return jsonify({"msg": "Missing JSON In Request"}), 400
    if not (validators.email(request.get_json()['email']) or
            validators.phone(request.get_json()['phone'])):
        return jsonify({"msg": "Invalid Phone Number or Email"}), 400

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

    # Connect to database
    db_connection = database.get()

    # Get a cursor
    cursor = db_connection.cursor()

    # Check if member already in table
    statement = 'SELECT name FROM members WHERE name=%s'
    cursor.execute(statement, (name,))
    member = cursor.fetchone()

    # Name field already exists
    if member:
        return jsonify({"msg": "Name Already Exists"}), 409
    # Name field doesn't exist so create a row
    else:
        statement = 'INSERT INTO members (name, email, phone) \
                    VALUES (%s, %s, %s)'
        cursor.execute(statement, (name, email, phone))
    db_connection.commit()
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
    if not validators.json(request):
        return jsonify({"msg": "Missing JSON In Request"}), 400
    member_id = request.get_json()['memberID']

    # Connect to database
    db_connection = database.get()

    # Get a cursor
    cursor = db_connection.cursor()

    # Query for row
    statement = 'SELECT name FROM members WHERE memberID=%s'
    cursor.execute(statement, (member_id,))
    member = cursor.fetchone()
    
    # Delete row if found
    if member:
        statement = 'DELETE FROM members WHERE memberID=%s'
        cursor.execute(statement, (member_id,))
        db_connection.commit()
        return jsonify({"msg": "success"}), 200
    return jsonify({"msg": "No Such Entry"}), 404


@app.route('/login', methods=['POST'])
def login() -> request:
    """ Accept login info and return JWT token """

    if not request.is_json:
        return jsonify({"msg": "Missing JSON In Request"}), 400

    username = request.get_json().get('username', None)
    password = request.get_json().get('password', None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    # Connect to database
    db_connection = database.get()

    # Get a cursor
    cursor = db_connection.cursor()

    # Query if user exists in table
    statement = 'SELECT * FROM users where username=%s'
    cursor.execute(statement, (username,))
    user = cursor.fetchone()

    # Generate an access token if user exists
    if user:
        db_password = user[2]
        # Wrong password
        if password != db_password:
            return jsonify({"msg": "Bad Username Or Password"}), 401
        # Success
        else:
            access_token = create_access_token(identity=[username, user[3]])
            return jsonify(access_token=access_token), 200
    # No such username
    else:
        return jsonify({"msg": "Bad Username Or Password"}), 401
