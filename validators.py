"""
Validation Helper Functions
"""
import re
from flask import request

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
