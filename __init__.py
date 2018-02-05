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

# Create application instance
app = Flask(__name__)
app.config['DEBUG'] = False


# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


### Component Imports
import trip_test.database
import trip_test.controllers
import trip_test.validators
#import trip_test.models
