from django.test import TestCase
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from userena.backends import UserenaAuthenticationBackend
from userena.models import UserenaUser

class UserenaAuthenticationBackendTests(TestCase):
    """
    Test the ``UserenaAuthenticationBackend`` which should return a ``User``
    when supplied with a username/email and a correct password.

    """
    fixtures = ['users',]
    backend = UserenaAuthenticationBackend()

    def test_with_username(self):
        """ Test the backend when usernames are supplied. """
        # Invalid usernames or passwords
        invalid_data_dicts = [
            # Invalid password
            {'identification': 'john',
             'password': 'inhalefish'},
            # Invalid username
            {'identification': 'alice',
             'password': 'blowfish'},
        ]
        for invalid_dict in invalid_data_dicts:
            result = self.backend.authenticate(identification=invalid_dict['identification'],
                                               password=invalid_dict['password'])
            self.failIf(isinstance(result, User))

        # Valid username and password
        result = self.backend.authenticate(identification='john',
                                           password='blowfish')
        self.failUnless(isinstance(result, User))

    def test_with_email(self):
        """ Test the backend when email address is supplied """
        # Invalid e-mail adressses or passwords
        invalid_data_dicts = [
            # Invalid password
            {'identification': 'john@example.com',
             'password': 'inhalefish'},
            # Invalid e-mail address
            {'identification': 'alice@example.com',
             'password': 'blowfish'},
        ]
        for invalid_dict in invalid_data_dicts:
            result = self.backend.authenticate(identification=invalid_dict['identification'],
                                               password=invalid_dict['password'])
            self.failIf(isinstance(result, User))

        # Valid e-email address and password
        result = self.backend.authenticate(identification='john@example.com',
                                           password='blowfish')
        self.failUnless(isinstance(result, User))

    def test_returns_userena_user(self):
        """
        Test that the ``UserenaAuthenticationBackend`` returns a
        ``UserenaUser`` and not the ``User``.

        """
        # Get an user
        user = self.backend.get_user(user_id=1)
        self.failUnless(isinstance(user, UserenaUser))

        # There is no user, like in the matrix, where there are no spoons.
        self.failIf(self.backend.get_user(user_id=99))
