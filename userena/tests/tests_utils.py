from urlparse import urlparse, parse_qs

from django.test import TestCase
from django.conf import settings

from userena.utils import (get_gravatar, signin_redirect, get_profile_model,
                           get_protocol, get_user_model)
from userena import settings as userena_settings
from userena.compat import SiteProfileNotAvailable

import hashlib

class UtilsTests(TestCase):
    """ Test the extra utils methods """
    fixtures = ['users']

    def test_get_gravatar(self):
        template = 's=%(size)s&d=%(type)s'

        # Check the defaults.
        parsed = urlparse(get_gravatar('alice@example.com'))
        self.failUnlessEqual(
            parse_qs(parsed.query),
            parse_qs(template % {'size': 80, 'type': 'identicon'})
        )

        # Check different size
        parsed = urlparse(get_gravatar('alice@example.com', size=200))
        self.failUnlessEqual(
            parse_qs(parsed.query),
            parse_qs(template % {'size': 200, 'type': 'identicon'})
        )

        # Check different default
        parsed = urlparse(get_gravatar('alice@example.com', default='404'))
        self.failUnlessEqual(
            parse_qs(parsed.query),
            parse_qs(template % {'size': 80, 'type': '404'})
        )

    def test_signin_redirect(self):
        """
        Test redirect function which should redirect the user after a
        succesfull signin.

        """
        # Test with a requested redirect
        self.failUnlessEqual(signin_redirect(redirect='/accounts/'), '/accounts/')

        # Test with only the user specified
        user = get_user_model().objects.get(pk=1)
        self.failUnlessEqual(signin_redirect(user=user),
                             '/accounts/%s/' % user.username)

        # The ultimate fallback, probably never used
        self.failUnlessEqual(signin_redirect(), settings.LOGIN_REDIRECT_URL)

    def test_get_profile_model(self):
        """
        Test if the correct profile model is returned when
        ``get_profile_model()`` is called.

        """
        # A non existent model should also raise ``SiteProfileNotAvailable``
        # error.
        with self.settings(AUTH_PROFILE_MODULE='userena.FakeProfile'):
            self.assertRaises(SiteProfileNotAvailable, get_profile_model)

        # An error should be raised when there is no ``AUTH_PROFILE_MODULE``
        # supplied.
        with self.settings(AUTH_PROFILE_MODULE=None):
            self.assertRaises(SiteProfileNotAvailable, get_profile_model)

    def test_get_protocol(self):
        """ Test if the correct protocol is returned """
        self.failUnlessEqual(get_protocol(), 'http')

        userena_settings.USERENA_USE_HTTPS = True
        self.failUnlessEqual(get_protocol(), 'https')
        userena_settings.USERENA_USE_HTTPS = False
