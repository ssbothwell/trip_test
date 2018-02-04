import os
import unittest
import json
import tempfile
import trip_test
from flask import request, Response


class Request:
    """
    Fake request for testing json validator
    """
    def __init__(self):
        self.method = 'GET'
        self.json = { 'memberID': 1}


class ValidatorsTestCases(unittest.TestCase):
    def test_json_a(self):
        """
        json validator success test
        Uses a GET request
        """
        resp = Request()
        self.assertTrue(trip_test.validators.json(resp))


    def test_json_b(self):
        """
        json validator failure test
        Uses a GET request wrong json data
        """
        resp = Request()
        resp.json = {'foo': 'bar'}
        self.assertFalse(trip_test.validators.json(resp))


    def test_json_c(self):
        """
        json validator success test
        Uses a PUT request
        """
        resp = Request()
        resp.method = 'PUT'
        resp.json = {'name': 'foo', 
                     'phone': '8001234567', 
                     'email': 'foo@bar.baz'
                    }
        self.assertTrue(trip_test.validators.json(resp))


    def test_json_d(self):
        """
        json validator failure test
        Uses a PUT request
        """
        resp = Request()
        resp.method = 'PUT'
        resp.json = {'foo': 'foo', 
                     'phone': '8001234567', 
                     'email': 'foo@bar.baz'
                    }
        self.assertFalse(trip_test.validators.json(resp))


    def test_email_a(self):
        """
        email validator success test
        """
        email = "foo@bar.baz"
        self.assertTrue(trip_test.validators.email(email))


    def test_email_b(self):
        """
        email validator failure test
        Does not contain `@`
        """
        email = "foo.com"
        self.assertFalse(trip_test.validators.email(email))


    def test_email_c(self):
        """
        email validator failure test
        Does not contain `.`
        """
        email = "foo@bar"
        self.assertFalse(trip_test.validators.email(email))


    def test_phone_a(self):
        """
        phone validator success test
        """
        number = "8001234567"
        self.assertTrue(trip_test.validators.phone(number))


    def test_phone_b(self):
        """
        phone validator failure test
        number too short
        """
        number = "1"
        self.assertFalse(trip_test.validators.phone(number))


    def test_phone_c(self):
        """
        phone validator failure test
        number contains letters 
        """
        number = "800123456A"
        self.assertFalse(trip_test.validators.phone(number))


class ControllersTestCases(unittest.TestCase):
    def setUp(self):
        # Create temp database
        self.db_fd, trip_test.app.config['DATABASE'] = tempfile.mkstemp()
        trip_test.app.testing = True
        self.app = trip_test.app.test_client()
        with trip_test.app.app_context():
            trip_test.database.init()
        
        # Load an initial mock member
        name = 'initial user'
        email = 'initial@user.foo'
        phone = '9999999999'
        mock_data = dict(name=name, email=email, phone=phone)

        self.put_helper('admin_user', mock_data)


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(trip_test.app.config['DATABASE'])


    def login(self, username: str, password: str)-> str:
        """
        Helper function for user auth. Takes a
        `username` and `password` and returns
        a JWT token.
        """
        
        headers = {'content-type': 'application/json'}
        response = self.app.post('/login', 
                 data=json.dumps(dict(username=username, password=password)),
                 headers=headers)
        json_response = json.loads(response.get_data(as_text=True))
        if 'access_token' in json_response: 
            return json_response['access_token']
        else:
            return json_response['msg']


    def put_helper(self, user: str, data: dict) -> dict:
        """
        Insert a row into members table using a 
        put request. Returns the response.
        """
        # Login
        access_token = self.login(user, 'password')


        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.put('/',
                                data=json.dumps(data),
                                headers=headers)
        return response


    def test_login_a(self):
        """
        login controller success test.
        """

        access_token = self.login('admin_user', 'password')
        self.assertNotEqual(access_token, 'Bad Username Or Password')


    def test_login_b(self):
        """
        login controller failure test.
        Bad username
        """

        access_token = self.login('foobar', 'password')
        self.assertEqual(access_token, 'Bad Username Or Password')


    def test_login_b(self):
        """
        login controller failure test.
        Bad password
        """

        access_token = self.login('admin_user', 'foobar')
        self.assertEqual(access_token, 'Bad Username Or Password')


    def test_get_entry_a(self):
        """ 
        get_entry controller success test.
        """

        # Login
        access_token = self.login('admin_user', 'password')

        # Generate request
        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.get('/',
                                data=json.dumps(dict(memberID='1')),
                                headers=headers)
        with self.subTest():
            self.assertEqual(response.status_code, 200)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['name'], 'initial user')


    def test_get_entry_b(self):
        """ 
        get_entry controller failure test.
        User has wrong access privilege.
        """

        # Login
        access_token = self.login('nothing_user', 'password')

        # Generate request
        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.get('/',
                                data=json.dumps(dict(memberID='1')),
                                headers=headers)
        with self.subTest():
            self.assertEqual(response.status_code, 403)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['msg'], 'Access Denied')


    def test_get_entry_c(self):
        """ 
        get_entry controller failure test.
        No such `memberID`
        """

        # Login
        access_token = self.login('admin_user', 'password')

        # Generate request
        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.get('/',
                                data=json.dumps(dict(memberID='11')),
                                headers=headers)
        with self.subTest():
            self.assertEqual(response.status_code, 400)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['msg'], 'No Such User')


    def test_add_entry_a(self):
        """
        add_entry controller success test.
        """

        # Mock member data
        name = 'foobar'
        email = 'foo@bar.baz'
        phone = '8001234567'
        mock_data = dict(name=name, email=email, phone=phone)

        response = self.put_helper('admin_user', mock_data)
        self.assertEqual(response.status_code, 201)


    def test_add_entry_b(self):
        """
        add_entry controller failure test.
        User has wrong access privilege.
        """

        # Mock member data
        name = 'foobar'
        email = 'foo@bar.baz'
        phone = '8001234567'
        mock_data = dict(name=name, email=email, phone=phone)

        response = self.put_helper('get_user', mock_data)
        with self.subTest():
            self.assertEqual(response.status_code, 200)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['msg'], 'Access Denied')

    
    def test_add_entry_c(self):
        """
        add_entry controller failure test.
        Duplicate member name.
        """

        # Mock member data
        name = 'initial user'
        email = 'foo@bar.baz'
        phone = '8001234567'
        mock_data = dict(name=name, email=email, phone=phone)

        response = self.put_helper('admin_user', mock_data)
        with self.subTest():
            self.assertEqual(response.status_code, 409)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['msg'], 'Name Already Exists')


    def test_delete_entry_a(self):
        """
        delete_entry controller success test.
        """

        # Login
        access_token = self.login('admin_user', 'password')

        # Generate request
        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.delete('/',
                                data=json.dumps(dict(memberID='1')),
                                headers=headers)
        with self.subTest():
            self.assertEqual(response.status_code, 200)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['msg'], 'success')


    def test_delete_entry_b(self):
        """
        delete_entry controller failure test.
        User has wrong access privilege.
        """

        # Login
        access_token = self.login('nothing_user', 'password')

        # Generate request
        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.delete('/',
                                data=json.dumps(dict(memberID='1')),
                                headers=headers)
        with self.subTest():
            self.assertEqual(response.status_code, 200)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['msg'], 'Access Denied')


    def test_delete_entry_c(self):
        """
        delete_entry controller failure test.
        No such `memberID`
        """

        # Login
        access_token = self.login('admin_user', 'password')

        # Generate request
        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.delete('/',
                                data=json.dumps(dict(memberID='8')),
                                headers=headers)
        with self.subTest():
            self.assertEqual(response.status_code, 404)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response['msg'], 'No Such Entry')


if __name__ == '__main__':
    unittest.main()
