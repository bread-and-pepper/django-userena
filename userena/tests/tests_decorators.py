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
