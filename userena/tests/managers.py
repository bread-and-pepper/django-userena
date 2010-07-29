from django.test import TestCase
from django.core import mail

from userena.models import Account
from userena import settings as userena_settings

import datetime, re

class AccountManagerTests(TestCase):
    """ Test the manager of Account """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    def test_create_inactive_user(self):
        """
        Test the creation of a new user.

        ``Account.create_inactive_user`` should create a new user that is set to active.
        It should also create a new account for this user.

        """
        new_user = Account.objects.create_inactive_user(**self.user_info)
        self.assertEqual(new_user.username, self.user_info['username'])
        self.assertEqual(new_user.email, self.user_info['email'])
        self.failUnless(new_user.check_password(self.user_info['password']))
        self.failIf(new_user.is_active)
        self.failUnlessEqual(Account.objects.filter(user__email=self.user_info['email']).count(), 1)

    def test_create_account(self):
        """
        Test the creation of a new account.

        ``Account.objects.create_account`` should create a new account for this user.
        The user is not activied yet therefore should get an e-mail which
        contains the ``activation_key``.

        """
        new_user = Account.objects.create_inactive_user(**self.user_info)

        account = Account.objects.get(user__email=self.user_info['email'])

        self.assertEqual(account.user.email, self.user_info['email'])
        self.assertEqual(new_user.account.user.id, new_user.id)
        self.failUnless(re.match('^[a-f0-9]{40}$', account.activation_key))

    def test_activation_valid(self):
        """

        Activation of the user with a valid ``activation_key`` should
        activate the user and set a new invalid ``activation_key`` that is
        defined in the setting ``USERENA_ACTIVIED``.

        """
        account = Account.objects.create_inactive_user(**self.user_info).account
        active_account = Account.objects.activate_user(account.activation_key)

        # The returned account should be the same as the one just created.
        self.failUnlessEqual(account, active_account)

        # The user should now be active.
        self.failUnless(active_account.user.is_active)

        # The activation key should be the same as in the settings
        self.assertEqual(active_account.activation_key, userena_settings.USERENA_ACTIVATED)

    def test_activation_invalid(self):
        """
        Activation with a key that's invalid should make
        ``Account.objects.activate_user`` return ``False``.

        """

        # Completely wrong key
        self.failIf(Account.objects.activate_user('wrong_key'))

        # At least the right length
        invalid_key = 10 * 'a1b2'
        self.failIf(Account.objects.activate_user(invalid_key))

    def test_activation_expired(self):
        """
        Activation with a key that's expired should also make
        ``Account.objects.activation_account`` return ``False``.

        """
        account = Account.objects.create_inactive_user(**self.user_info).account

        # Set the date that the key is created a day further away than allowed
        account.activation_key_created -= datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS + 1)
        account.save()

        # Try to verify the account
        Account.objects.activate_user(account.activation_key)

        active_account = Account.objects.get(user__username='alice')

        # Account activation should have failed
        self.failIf(active_account.user.is_active)

        # The activation key should still be a hash
        self.assertEqual(account.activation_key, active_account.activation_key)


    def test_delete_expired_users(self):
        """
        Test if expired users are deleted from the database.

        """
        expired_account = Account.objects.create_inactive_user(**self.user_info).account
        expired_account.activation_key_created -= datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS + 1)
        expired_account.save()

        deleted_users = Account.objects.delete_expired_users()

        self.failUnlessEqual(deleted_users[0].username, 'alice')
