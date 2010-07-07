from django.test import TestCase
from django.contrib.auth.models import User

from userina.models import Account

class AccountModelTests(TestCase):
    """ Test the model and manager of Account """
    user_username = 'alice'
    user_password= 'swordfish'
    user_email = 'alice@example.com'

    fixtures = ['users.json', 'accounts.json']

    def test_age_property(self):
        """ Test if the ``user.age`` returns the correct age. """
        account = Account.objects.get(pk=1)
        self.assertEqual(account.age, 27)

    def test_get_account(self):
        """
        Test if ``user.account`` always returns the account for the user.

        """
        user_with_account = User.objects.get(pk=1)
        user_without_account = User.objects.get(pk=2)

        # Account should be the account model for a user who already has an
        # account.
        self.assertEqual(type(user_with_account.account), Account)

        # Account should be created when a user has no account
        self.assertEqual(type(user_without_account.account), Account)

    def test_create_user(self):
        """
        Test the creation of a new user.

        ``Account.create_user`` should create a new user that is set to active.

        """
        new_user = Account.objects.create_user(self.user_username,
                                               self.user_email,
                                               self.user_password)
        self.assertEqual(new_user.username, 'alice')
        self.assertEqual(new_user.email, 'alice@example.com')
        self.failUnless(new_user.check_password('swordfish'))
        self.failUnless(new_user.is_active)

    def test_verification_email(self):
        """
        When a new account is created, a verification e-mail should be send out
        by ``Account.send_verification_email``.

        """
        new_account = Account.objects.create_user(self.user_username,
                                                  self.user_email,
                                                  self.user_password)

    def test_create_account(self):
        """
        Test the creation of a new account.

        ``Account.create_account`` should create a new account for this user.
        The user is not verified yet therefore should get an e-mail which
        contains the ``verification_key``.

        """
        pass
