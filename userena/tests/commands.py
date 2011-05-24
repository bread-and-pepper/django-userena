from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User, Permission

from userena.models import UserenaSignup
from userena.managers import ASSIGNED_PERMISSIONS
from userena import settings as userena_settings

from guardian.shortcuts import remove_perm
from guardian.models import UserObjectPermission

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

class CheckPermissionTests(TestCase):
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    def test_check_permissions(self):
        # Create a new account.
        user = UserenaSignup.objects.create_inactive_user(**self.user_info)
        user.save()

        # Remove all permissions
        UserObjectPermission.objects.filter(user=user).delete()
        self.failUnlessEqual(UserObjectPermission.objects.filter(user=user).count(),
                             0)

        # Check it
        call_command('check_permissions')

        # User should have all permissions again
        user_permissions = UserObjectPermission.objects.filter(user=user).values_list('permission__codename', flat=True)

        required_permissions = [u'change_user', u'delete_user', u'change_profile', u'view_profile']
        for perm in required_permissions:
            if perm not in user_permissions:
                self.fail()

        # Check it again should do nothing
        call_command('check_permissions')

    def test_incomplete_permissions(self):
        # Delete the neccesary permissions
        for model, perms in ASSIGNED_PERMISSIONS.items():
            for perm in perms:
                Permission.objects.get(name=perm[1]).delete()

        # Check if they are they are back
        for model, perms in ASSIGNED_PERMISSIONS.items():
            for perm in perms:
                try:
                    perm = Permission.objects.get(name=perm[1])
                except Permission.DoesNotExist: pass
                else: self.fail()

        # Repair them
        call_command('check_permissions')

        # Check if they are they are back
        for model, perms in ASSIGNED_PERMISSIONS.items():
            for perm in perms:
                try:
                    perm = Permission.objects.get(name=perm[1])
                except Permission.DoesNotExist:
                    self.fail()
