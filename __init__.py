"""
Tripp Inc Backend Exercise
Solomon Bothwell

A basic REST interface to a sqlite database with JWT
authorization.
"""
import os
from flask import Flask
from flask_jwt_extended import JWTManager

### Configuration

# Create application instance and load config
app = Flask(__name__)
app.config.from_object(__name__)


# Default config
# secret keys and database user info MUST be overwritten
# on production server using environment variables
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


### Project Imports
import trip_test.database
import trip_test.controllers
import trip_test.validators
#import trip_test.models
