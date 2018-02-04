import os
import trip_test
import unittest
import tempfile
from flask import request
import json


class TripTestCase(unittest.TestCase):
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
        return  json_response['access_token']


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
