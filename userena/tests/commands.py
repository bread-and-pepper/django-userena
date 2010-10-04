from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User

from userena.models import UserenaSignup
from userena import settings as userena_settings

import datetime

class CleanExpiredTests(TestCase):
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    def test_clean_expired(self):
        """
        Test if ``clean_expired`` deletes all users which ``activation_key``
        is expired.

        """
        # Create an account which is expired.
        user = UserenaSignup.objects.create_inactive_user(**self.user_info)
        user.date_joined -= datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS + 1)
        user.save()

        # There should be one account now
        User.objects.get(username=self.user_info['username'])

        # Clean it.
        call_command('clean_expired')

        self.failUnlessEqual(User.objects.filter(username=self.user_info['username']).count(), 0)
