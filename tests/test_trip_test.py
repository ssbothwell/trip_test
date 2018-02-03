import os
import trip_test
import unittest
import tempfile
import json

class TripTestCase(unittest.TestCase):
    def setUp(self):
        # Create temp database
        self.db_fd, trip_test.app.config['DATABASE'] = tempfile.mkstemp()
        trip_test.app.testing = True
        self.app = trip_test.app.test_client()
        with trip_test.app.app_context():
            trip_test.trip_test.init_db()


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(trip_test.app.config['DATABASE'])

    def login(self, username, password):
        headers = {'content-type': 'application/json'}
        response = self.app.post('/login', 
                 data=json.dumps(dict(username=username, password=password)),
                 headers=headers)
        json_response = json.loads(response.get_data(as_text=True))
        return  json_response['access_token']

    def test_putA(self):
        """ test put request success with admin user account """

        # Login
        access_token = self.login('admin_user', 'password')

        # Mock member data
        name = 'foobar'
        email = 'foo@bar.baz'
        phone = '8001234567'

        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.put('/',
                                data=json.dumps(dict(name=name,
                                                     email=email,
                                                     phone=phone)),
                                headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_putB(self):
        """ test put request failure with unprivileged user account """

        # Login
        access_token = self.login('get_user', 'password')

        # Mock member data
        name = 'foobar'
        email = 'foo@bar.baz'
        phone = '8001234567'

        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer %s' % access_token}
        response = self.app.put('/',
                                data=json.dumps(dict(name=name,
                                                     email=email,
                                                     phone=phone)),
                                headers=headers)
        with self.subTest():
            self.assertEqual(response.status_code, 200)
        with self.subTest():
            json_response = json.loads(response.get_data(as_text=True))
            self.assertEqual(json_response[0]['msg'], 'Access Denied')


if __name__ == '__main__':
    unittest.main()
