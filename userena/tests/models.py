from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.core import mail
from django.conf import settings

from userena.models import UserenaUser, Profile, upload_to_mugshot
from userena import settings as userena_settings

import datetime, hashlib, re

MUGSHOT_RE = re.compile('^[a-f0-9]{40}$')

class UserenaUserModelTests(TestCase):
    """ Test the model of UserenaUser """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    fixtures = ['users.json']

    def test_upload_mugshot(self):
        """
        Test the uploaded path of mugshots

        TODO: What if a image get's uploaded with no extension?

        """
        user = UserenaUser.objects.get(pk=1)
        filename = 'my_avatar.png'
        path = upload_to_mugshot(user, filename)

        # Path should be changed from the original
        self.failIfEqual(filename, path)

        # Check if the correct path is returned
        MUGSHOT_RE = re.compile('^%(mugshot_path)s[a-f0-9]{10}.png$' %
                                {'mugshot_path': userena_settings.USERENA_MUGSHOT_PATH})

        self.failUnless(MUGSHOT_RE.search(path))

    def test_stringification(self):
        """
        Test the stringification of a ``UserenaUser`` object. A "human-readable"
        representation of an ``UserenaUser`` object.

        """
        account = UserenaUser.objects.get(pk=1)
        self.failUnlessEqual(account.__unicode__(),
                             account.user.username)

    def test_get_absolute_url(self):
        """ Test if the ``get_absolute_url`` function returns the proper URI """
        account = UserenaUser.objects.get(pk=1)
        self.failUnlessEqual(account.get_absolute_url(),
                             reverse('userena_profile_detail',
                                     kwargs={'username': account.user.username}))


    def test_change_email(self):
        """ TODO """
        pass

    def test_activation_expired_account(self):
        """
        ``UserenaUser.activation_key_expired()`` is ``True`` when the
        ``activation_key_created`` is more days ago than defined in
        ``USERENA_ACTIVATION_DAYS``.

        """
        user = UserenaUser.objects.create_inactive_user(**self.user_info)
        user.activation_key_created -= datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS + 1)
        user.save()

        user = UserenaUser.objects.get(username='alice')
        self.failUnless(user.activation_key_expired())

    def test_activation_used_account(self):
        """
        An account cannot be activated anymore once the activation key is
        already used.

        """
        user = UserenaUser.objects.create_inactive_user(**self.user_info)
        activated_user = UserenaUser.objects.activate_user(user.activation_key)
        self.failUnless(activated_user.activation_key_expired())

    def test_activation_unexpired_account(self):
        """
        ``UserenaUser.activation_key_expired()`` is ``False`` when the
        ``activation_key_created`` is within the defined timeframe.``

        """
        user = UserenaUser.objects.create_inactive_user(**self.user_info)
        self.failIf(user.activation_key_expired())

    def test_activation_email(self):
        """
        When a new account is created, a activation e-mail should be send out
        by ``UserenaUser.send_activation_email``.

        """
        new_user = UserenaUser.objects.create_inactive_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])


class ProfileModelTest(TestCase):
    """ Test the ``Profile`` model """
    fixtures = ['users.json', 'profiles.json']

    def test_age_property(self):
        """ Test if the ``user.age`` returns the correct age. """
        profile = Profile.objects.get(pk=1)
        self.assertEqual(profile.age, 27)

    def test_mugshot_url(self):
        """ The user has uploaded it's own mugshot. This should be returned. """
        profile = Profile.objects.get(pk=1)
        profile.mugshot = 'fake_image.png'
        profile.save()

        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.get_mugshot_url(),
                             settings.MEDIA_URL + 'fake_image.png')

    def test_get_mugshot_url_without_gravatar(self):
        """
        Test if the correct mugshot is returned for the user when
        ``USERENA_MUGSHOT_GRAVATAR`` is set to ``False``.

        """
        # This user has no mugshot, and gravatar is disabled. And to make
        # matters worse, there isn't even a default image.
        userena_settings.USERENA_MUGSHOT_GRAVATAR = False
        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.get_mugshot_url(), None)

        # There _is_ a default image
        userena_settings.USERENA_MUGSHOT_DEFAULT = 'http://example.com'
        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.get_mugshot_url(), 'http://example.com')

        # Settings back to default
        userena_settings.USERENA_MUGSHOT_GRAVATAR = True

    def test_get_mugshot_url_with_gravatar(self):
        """
        Test if the correct mugshot is returned when the user makes use of gravatar.

        """
        template = 'http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(default)s'
        profile = Profile.objects.get(pk=1)

        gravatar_hash = hashlib.md5(profile.user.email).hexdigest()

        # Test with the default settings
        self.failUnlessEqual(profile.get_mugshot_url(),
                             template % {'hash': gravatar_hash,
                                         'size': userena_settings.USERENA_MUGSHOT_SIZE,
                                         'default': userena_settings.USERENA_MUGSHOT_DEFAULT})

        # Change userena settings
        userena_settings.USERENA_MUGSHOT_SIZE = 180
        userena_settings.USERENA_MUGSHOT_DEFAULT = '404'

        self.failUnlessEqual(profile.get_mugshot_url(),
                             template % {'hash': gravatar_hash,
                                         'size': userena_settings.USERENA_MUGSHOT_SIZE,
                                         'default': userena_settings.USERENA_MUGSHOT_DEFAULT})

        # Settings back to default
        userena_settings.USERENA_MUGSHOT_SIZE = 80
        userena_settings.USERENA_MUGSHOT_DEFAULT = 'identicon'
