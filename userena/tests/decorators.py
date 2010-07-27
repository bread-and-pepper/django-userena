from django.test import TestCase
from django.core.urlresolvers import reverse

from userena.utils import get_gravatar
from userena import settings as userena_settings

import re

class DecoratorTests(TestCase):
    """ Test the decorators """

    def test_secure_required(self):
        """
        Test that the ``secure_required`` decorator does a permanent redirect
        to a secured page.

        """
        userena_settings.USERENA_USE_HTTPS = True
        response = self.client.get(reverse('userena_signin'))

        # Test for the permanent redirect
        self.assertEqual(response.status_code, 301)

        # Test if the redirected url contains 'https'. Couldn't use
        # ``assertRedirects`` here because the redirected to page is
        # non-existant.
        self.assertTrue('https' in str(response))

        # Set back to the old settings
        userena_settings.USERENA_USE_HTTPS = False

    def test_http_x_forwarded_ssl(self):
        """
        Test that if ``HTTP_X_FORWARDED_SSL`` is in ``request.META`` the
        request is thought to be secure

        I believe that this fix was required on some hosting providers who use
        proxies.

        """
        userena_settings.USERENA_USE_HTTPS = True
        response = self.client.get(reverse('userena_signin'), **{'HTTP_X_FORWARDED_SSL':'on'})

        # We shouldn't get a redirect this time.
        self.assertEqual(response.status_code, 200)

        # Back to the old.
        userena_settings.USERENA_USE_HTTPS = False
