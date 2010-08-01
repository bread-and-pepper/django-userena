from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.core import mail
from django.conf import settings

from userena.models import Account, upload_to_mugshot
from userena import settings as userena_settings

import datetime, hashlib, re

MUGSHOT_RE = re.compile('^[a-f0-9]{40}$')

class AccountModelTests(TestCase):
    """ Test the model of Account """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    fixtures = ['users.json', 'accounts.json']

    def test_upload_mugshot(self):
        """
        Test the uploaded path of mugshots

        TODO: What if a image get's uploaded with no extension?

        """
        account = Account.objects.get(pk=1)
        filename = 'my_avatar.png'
        path = upload_to_mugshot(account, filename)

        # Path should be changed from the original
        self.failIfEqual(filename, path)

        # Check if the correct path is returned
        MUGSHOT_RE = re.compile('^%(mugshot_path)s[a-f0-9]{10}.png$' %
                                {'mugshot_path': userena_settings.USERENA_MUGSHOT_PATH})

        self.failUnless(MUGSHOT_RE.search(path))

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

    def test_stringification(self):
        """
        Test the stringification of a ``Account`` object. A "human-readable"
        representation of an ``Account`` object.

        """
        account = Account.objects.get(pk=1)
        self.failUnlessEqual(account.__unicode__(),
                             account.user.username)

    def test_get_absolute_url(self):
        """ Test if the ``get_absolute_url`` function returns the proper URI """
        account = Account.objects.get(pk=1)
        self.failUnlessEqual(account.get_absolute_url(),
                             reverse('userena_detail',
                                     kwargs={'username': account.user.username}))

    def test_activity_property(self):
        """ TODO: Test the activity property """
        pass

    def test_age_property(self):
        """ Test if the ``user.age`` returns the correct age. """
        account = Account.objects.get(pk=1)
        self.assertEqual(account.age, 27)

    def test_change_email(self):
        """ TODO """
        pass

    def test_expired_account(self):
        """
        ``Account.activation_key_expired()`` is ``True`` when the
        ``activation_key_created`` is more days ago than defined in
        ``USERENA_ACTIVATION_DAYS``.

        """
        account = Account.objects.create_inactive_user(**self.user_info).account
        account.activation_key_created -= datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS + 1)
        account.save()

        account = Account.objects.get(user__username='alice')
        self.failUnless(account.activation_key_expired())

    def test_unexpired_account(self):
        """
        ``Account.activation_key_expired()`` is ``False`` when the
        ``activation_key_created`` is within the defined timeframe.``

        """
        account = Account.objects.create_inactive_user(**self.user_info).account
        self.failIf(account.activation_key_expired())

    def test_activation_key_almost_expired(self):
        """ TODO """
        pass

    def test_activation_email(self):
        """
        When a new account is created, a activation e-mail should be send out
        by ``Account.send_activation_email``.

        """
        new_user = Account.objects.create_inactive_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_notification_expired_email(self):
        """
        Test if the notification is send out to people if there account is
        ``USERENA_ACTIVATION_NOTIFY_DAYS`` away from being deactivated.

        """
        account = Account.objects.create_inactive_user(**self.user_info).account
        window = userena_settings.USERENA_ACTIVATION_DAYS - userena_settings.USERENA_ACTIVATION_NOTIFY_DAYS
        account.activation_key_created -= datetime.timedelta(days=window)
        account.save()

        # Send out notifications
        notifications = Account.objects.notify_almost_expired()

        account = Account.objects.get(user__username=self.user_info['username'])
        # Two e-mails have been send out, 1 activation, 1 notification
        self.failUnlessEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])
        # Account should now be set as notified
        self.failUnless(account.activation_notification_send)

        # There should be no more notifications
        self.failUnlessEqual(len(Account.objects.notify_almost_expired()), 0)

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

        # Settings back to default
        userena_settings.USERENA_MUGSHOT_GRAVATAR = True

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

        # Settings back to default
        userena_settings.USERENA_MUGSHOT_SIZE = 80
        userena_settings.USERENA_MUGSHOT_DEFAULT = 'identicon'
