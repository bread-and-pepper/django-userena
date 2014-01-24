from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.core import mail
from django.conf import settings
from django.test import TestCase

from userena.models import UserenaSignup, upload_to_mugshot
from userena import settings as userena_settings
from userena.tests.profiles.models import Profile
from userena.utils import get_user_model

import datetime, hashlib, re

User = get_user_model()

MUGSHOT_RE = re.compile('^[a-f0-9]{40}$')

class UserenaSignupModelTests(TestCase):
    """ Test the model of UserenaSignup """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    fixtures = ['users', 'profiles']

    def test_upload_mugshot(self):
        """
        Test the uploaded path of mugshots

        TODO: What if a image get's uploaded with no extension?

        """
        user = User.objects.get(pk=1)
        filename = 'my_avatar.png'
        path = upload_to_mugshot(user.get_profile(), filename)

        # Path should be changed from the original
        self.failIfEqual(filename, path)

        # Check if the correct path is returned
        MUGSHOT_RE = re.compile('^%(mugshot_path)s[a-f0-9]{10}.png$' %
                                {'mugshot_path': userena_settings.USERENA_MUGSHOT_PATH})

        self.failUnless(MUGSHOT_RE.search(path))

    def test_stringification(self):
        """
        Test the stringification of a ``UserenaSignup`` object. A
        "human-readable" representation of an ``UserenaSignup`` object.

        """
        signup = UserenaSignup.objects.get(pk=1)
        self.failUnlessEqual(signup.__unicode__(),
                             signup.user.username)

    def test_change_email(self):
        """ TODO """
        pass

    def test_activation_expired_account(self):
        """
        ``UserenaSignup.activation_key_expired()`` is ``True`` when the
        ``activation_key_created`` is more days ago than defined in
        ``USERENA_ACTIVATION_DAYS``.

        """
        user = UserenaSignup.objects.create_user(**self.user_info)
        user.date_joined -= datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS + 1)
        user.save()

        user = User.objects.get(username='alice')
        self.failUnless(user.userena_signup.activation_key_expired())

    def test_activation_used_account(self):
        """
        An user cannot be activated anymore once the activation key is
        already used.

        """
        user = UserenaSignup.objects.create_user(**self.user_info)
        activated_user = UserenaSignup.objects.activate_user(user.userena_signup.activation_key)
        self.failUnless(activated_user.userena_signup.activation_key_expired())

    def test_activation_unexpired_account(self):
        """
        ``UserenaSignup.activation_key_expired()`` is ``False`` when the
        ``activation_key_created`` is within the defined timeframe.``

        """
        user = UserenaSignup.objects.create_user(**self.user_info)
        self.failIf(user.userena_signup.activation_key_expired())

    def test_activation_email(self):
        """
        When a new account is created, a activation e-mail should be send out
        by ``UserenaSignup.send_activation_email``.

        """
        new_user = UserenaSignup.objects.create_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_plain_email(self):
        """
        If HTML emails are disabled, check that outgoing emails are not multipart
        """
        userena_settings.USERENA_HTML_EMAIL = False
        new_user = UserenaSignup.objects.create_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(unicode(mail.outbox[0].message()).find("multipart/alternative"),-1)

    def test_html_email(self):
        """
        If HTML emails are enabled, check outgoings emails are multipart and
        that different html and plain text templates are used
        """
        userena_settings.USERENA_HTML_EMAIL = True
        userena_settings.USERENA_USE_PLAIN_TEMPLATE = True

        new_user = UserenaSignup.objects.create_user(**self.user_info)

        # Reset configuration
        userena_settings.USERENA_HTML_EMAIL = False
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("multipart/alternative")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("text/plain")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("text/html")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("<html>")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("<p>Thank you for signing up")>-1)
        self.assertFalse(mail.outbox[0].body.find("<p>Thank you for signing up")>-1)

    def test_generated_plain_email(self):
        """
        If HTML emails are enabled and plain text template are disabled,
        check outgoings emails are multipart and that plain text is generated
        from html body
        """
        userena_settings.USERENA_HTML_EMAIL = True
        userena_settings.USERENA_USE_PLAIN_TEMPLATE = False

        new_user = UserenaSignup.objects.create_user(**self.user_info)

        # Reset configuration
        userena_settings.USERENA_HTML_EMAIL = False
        userena_settings.USERENA_USE_PLAIN_TEMPLATE = True

        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("multipart/alternative")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("text/plain")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("text/html")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("<html>")>-1)
        self.assertTrue(unicode(mail.outbox[0].message()).find("<p>Thank you for signing up")>-1)
        self.assertTrue(mail.outbox[0].body.find("Thank you for signing up")>-1)

class BaseProfileModelTest(TestCase):
    """ Test the ``BaseProfile`` model """
    fixtures = ['users', 'profiles']

    def test_mugshot_url(self):
        """ The user has uploaded it's own mugshot. This should be returned. """
        profile = Profile.objects.get(pk=1)
        profile.mugshot = 'fake_image.png'
        profile.save()

        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.get_mugshot_url(),
                             settings.MEDIA_URL + 'fake_image.png')

    def test_stringification(self):
        """ Profile should return a human-readable name as an object """
        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.__unicode__(),
                             'Profile of %s' % profile.user.username)

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
        template = '//www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(default)s'
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

    def test_get_full_name_or_username(self):
        """ Test if the full name or username are returned correcly """
        user = User.objects.get(pk=1)
        profile = user.get_profile()

        # Profile #1 has a first and last name
        full_name = profile.get_full_name_or_username()
        self.failUnlessEqual(full_name, "John Doe")

        # Let's empty out his name, now we should get his username
        user.first_name = ''
        user.last_name = ''
        user.save()

        self.failUnlessEqual(profile.get_full_name_or_username(),
                             "john")

        # Finally, userena doesn't use any usernames, so we should return the
        # e-mail address.
        userena_settings.USERENA_WITHOUT_USERNAMES = True
        self.failUnlessEqual(profile.get_full_name_or_username(),
                             "john@example.com")
        userena_settings.USERENA_WITHOUT_USERNAMES = False

    def test_can_view_profile(self):
        """ Test if the user can see the profile with three type of users. """
        anon_user = AnonymousUser()
        super_user = User.objects.get(pk=1)
        reg_user = User.objects.get(pk=2)

        profile = Profile.objects.get(pk=1)

        # All users should be able to see a ``open`` profile.
        profile.privacy = 'open'
        self.failUnless(profile.can_view_profile(anon_user))
        self.failUnless(profile.can_view_profile(super_user))
        self.failUnless(profile.can_view_profile(reg_user))

        # Registered and super users should be able to see a ``registered``
        # profile.
        profile.privacy = 'registered'
        self.failIf(profile.can_view_profile(anon_user))
        self.failUnless(profile.can_view_profile(super_user))
        self.failUnless(profile.can_view_profile(reg_user))

        # Only superusers can see a closed profile.
        profile.privacy = 'closed'
        self.failIf(profile.can_view_profile(anon_user))
        self.failUnless(profile.can_view_profile(super_user))
        self.failIf(profile.can_view_profile(reg_user))
