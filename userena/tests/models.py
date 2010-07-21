from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings

from userena.models import Account
from userena import settings as userena_settings

import re, datetime, hashlib

class AccountModelTests(TestCase):
    """ Test the model and manager of Account """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    fixtures = ['users.json', 'accounts.json']

    def test_get_absolute_url(self):
        """ Test if the ``get_absolute_url`` function returns the proper URI """
        account = Account.objects.get(pk=1)
        self.failUnlessEqual(account.get_absolute_url(), reverse('userena_me'))

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
        It should also create a new account for this user.

        """
        new_user = Account.objects.create_user(**self.user_info)
        self.assertEqual(new_user.username, self.user_info['username'])
        self.assertEqual(new_user.email, self.user_info['email'])
        self.failUnless(new_user.check_password(self.user_info['password']))
        self.failUnless(new_user.is_active)
        self.failUnlessEqual(Account.objects.filter(user__email=self.user_info['email']).count(), 1)

    def test_verification_email(self):
        """
        When a new account is created, a verification e-mail should be send out
        by ``Account.send_verification_email``.

        """
        new_user = Account.objects.create_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_create_account(self):
        """
        Test the creation of a new account.

        ``Account.objects.create_account`` should create a new account for this user.
        The user is not verified yet therefore should get an e-mail which
        contains the ``verification_key``.

        """
        new_user = User.objects.create_user(**self.user_info)
        new_account = Account.objects.create_account(new_user)

        self.assertEqual(Account.objects.filter(user__email=self.user_info['email']).count(), 1)
        self.assertEqual(new_account.user.id, new_user.id)
        self.failUnless(re.match('^[a-f0-9]{40}$', new_account.verification_key))

    def test_expired_account(self):
        """
        ``Account.verification_key_expired()`` is ``True`` when the
        ``verification_key_created`` is more days ago than defined in
        ``USERENA_VERIFICATION_DAYS``.

        """
        account = Account.objects.create_user(**self.user_info).account
        account.verification_key_created -= datetime.timedelta(days=userena_settings.USERENA_VERIFICATION_DAYS + 1)
        account.save()

        account = Account.objects.get(user__username='alice')
        self.failUnless(account.verification_key_expired())

    def test_unexpired_account(self):
        """
        ``Account.verification_key_expired()`` is ``False`` when the
        ``verification_key_created`` is within the defined timeframe.``

        """
        account = Account.objects.create_user(**self.user_info).account
        self.failIf(account.verification_key_expired())

    def test_get_verification_url(self):
        """
        Test the verification URL that is created by
        ``Account.get_verification_url``.

        """
        account = Account.objects.create_user(**self.user_info).account
        site = Site.objects.get_current()

        verification_url = 'http://%(domain)s%(path)s' % {'domain': site.domain,
                                                          'path': reverse('userena_verify',
                                                                           kwargs={'verification_key': account.verification_key})}
        self.failUnlessEqual(account.get_verification_url, verification_url)

    def test_verification_valid(self):
        """
        Verification of the account with a valid ``verification_key`` should
        verify the account and set a new invalid ``verification_key`` that is
        defined in the setting ``USERENA_VERIFIED``.

        """
        account = Account.objects.create_user(**self.user_info).account
        verified_account = Account.objects.verify_account(account.verification_key)

        # The returned account should be the same as the one just created.
        self.failUnlessEqual(account, verified_account)

        # The account should now be verified.
        self.failUnless(verified_account.is_verified)

        # The verification key should be the same as in the settings
        self.assertEqual(verified_account.verification_key, userena_settings.USERENA_VERIFIED)

    def test_verification_invalid(self):
        """
        Verification with a key that's invalid should make
        ``Account.objects.verify_account`` return ``False``.

        """
        self.failIf(Account.objects.verify_account('wrong_key'))

    def test_verification_expired(self):
        """
        Verification with a key that's expired should also make
        ``Account.objects.verify_account`` return ``False``.

        """
        account = Account.objects.create_user(**self.user_info).account

        # Set the date that the key is created a day further away than allowed
        account.verification_key_created -= datetime.timedelta(days=userena_settings.USERENA_VERIFICATION_DAYS + 1)
        account.save()

        # Try to verify the account
        Account.objects.verify_account(account.verification_key)

        verified_account = Account.objects.get(user__username='alice')

        # Account verification should have failed
        self.failIf(verified_account.is_verified)

        # The verification key should still be a hash
        self.assertEqual(account.verification_key, verified_account.verification_key)

    def test_delete_expired_users(self):
        """
        Test if expired users are deleted from the database.

        """
        expired_account = Account.objects.create_user(**self.user_info).account
        expired_account.verification_key_created -= datetime.timedelta(days=userena_settings.USERENA_VERIFICATION_DAYS + 1)
        expired_account.save()

        deleted_users = Account.objects.delete_expired_users()

        self.failUnlessEqual(deleted_users[0].username, 'alice')

    def test_notification_expired_users(self):
        """
        Test if the notification is send out to people if there account is
        ``USERENA_VERIFICATION_NOTIFY_DAYS`` away from being deactivated.

        """
        account = Account.objects.create_user(**self.user_info).account
        window = userena_settings.USERENA_VERIFICATION_DAYS - userena_settings.USERENA_VERIFICATION_NOTIFY_DAYS
        account.verification_key_created -= datetime.timedelta(days=window)
        account.save()

        notifications = Account.objects.notify_almost_expired()

        # Check if verification e-mail get's registered as send out.
        account = Account.objects.get(user__username=self.user_info['username'])
        self.failUnless(account.verification_notification_send)
        # Two e-mails have been send out, 1 registration, 1 notification
        self.failUnlessEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])
        # Account should now be set as notified
        self.failUnless(account.verification_notification_send)

        # There should be no more notifications
        self.failUnlessEqual(len(Account.objects.notify_almost_expired()), 0)

    def test_change_email(self):
        """
        A user can change their e-mail address. But this new e-mail address
        still needs to be verified.

        """
        account = Account.objects.get(user__email__iexact='john@example.com')

        # Let's change john's e-mail address.
        account.change_email('john@newexample.com')

        # ``Account.temporary_email`` should be set to the new e-mail address.
        self.failUnlessEqual(account.temporary_email, 'john@newexample.com')

        # There shoulde be a new verification key
        self.failIfEqual(account.verification_key,
                         userena_settings.USERENA_VERIFIED)
        # Check that the e-mail is send out
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['john@newexample.com'])


    def test_valid_change_email(self):
        """ Test a valid verification of a new e-mail """
        account = Account.objects.get(user__email__iexact='john@example.com')
        account.change_email('john@newexample.com')

        # Verify the email change
        verified_account = Account.objects.verify_account(account.verification_key)
        self.failUnlessEqual(account, verified_account)

        self.failUnlessEqual(verified_account.user.email, 'john@newexample.com')
        self.failUnlessEqual(verified_account.temporary_email, '')
        self.failUnlessEqual(verified_account.verification_key, userena_settings.USERENA_VERIFIED)


    def test_get_mugshot_url_without_gravatar(self):
        """
        Test if the correct mugshot is returned for the user when
        ``USERENA_MUGSHOT_GRAVATAR`` is set to ``False``.

        """
        # This user has no mugshot, and gravatar is disabled. And to make
        # matters worse, there isn't even a default image.
        userena_settings.USERENA_MUGSHOT_GRAVATAR = False
        account = Account.objects.get(pk=1)
        self.failUnlessEqual(account.get_mugshot_url(), None)

        # There _is_ a default image
        userena_settings.USERENA_MUGSHOT_DEFAULT = 'http://example.com'
        account = Account.objects.get(pk=1)
        self.failUnlessEqual(account.get_mugshot_url(), 'http://example.com')

    def test_get_mugshot_url_with_gravatar(self):
        """
        Test if the correct mugshot is returned when the user makes use of gravatar.

        """
        template = 'http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(default)s'
        account = Account.objects.get(pk=1)

        gravatar_hash = hashlib.md5(account.user.email).hexdigest()

        # Test with the default settings
        self.failUnlessEqual(account.get_mugshot_url(),
                             template % {'hash': gravatar_hash,
                                         'size': userena_settings.USERENA_MUGSHOT_SIZE,
                                         'default': userena_settings.USERENA_MUGSHOT_DEFAULT})

        # Change userena settings
        userena_settings.USERENA_MUGSHOT_SIZE = 180
        userena_settings.USERENA_MUGSHOT_DEFAULT = '404'

        self.failUnlessEqual(account.get_mugshot_url(),
                             template % {'hash': gravatar_hash,
                                         'size': userena_settings.USERENA_MUGSHOT_SIZE,
                                         'default': userena_settings.USERENA_MUGSHOT_DEFAULT})
