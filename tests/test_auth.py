from unittest.mock import patch
from pyverless.auth import authenticate

from config_test.models import User


class TestAuth():

    def setup_class(self):
        self.context = None

        # A user
        self.user = User(email='user@users.com', password='test-password')

    @patch('pyverless.auth.get_user_by_email')
    def test_authenticate(self, mock_user):

        mock_user.return_value = self.user

        # Test succesful authentication
        assert authenticate('user@users.com', 'test-password')

        # Test unsuccesful authentication. Wrong password
        assert not authenticate('user@users.com', 'not-my-test-password')

        mock_user.return_value = None

        # Test unsuccesful authentication. No user exists with the given password
        assert not authenticate('not_a_user@users.com', 'test-password')
