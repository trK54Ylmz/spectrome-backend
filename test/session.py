from unittest import TestCase
from db.model import User
from server.session import Session


class SessionTest(TestCase):
    def test_session_create(self):
        user = User()
        user.uid = 1e10
        user.name = 'John Doe'
        user.email = 'john.doe@example.com'

        session_code = Session.create(user)

        self.assertIsNotNone(session_code)
