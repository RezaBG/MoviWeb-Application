import unittest

from moviweb_app import app, db
from datamanager.models import User, Movie

class MoviWebAppRouteTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///memory:"
        self.client = app.test_client()

        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to MoviWeb', response.data)

    def test_add_user_get(self):
        response = self.client.get('/add_user')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New User', response.data)

    def test_add_user_post(self):
        response = self.client.post('/add_user', data={"name": "TestUser"}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User added successfully', response.data)


if __name__ == '__main__':
    unittest.main()