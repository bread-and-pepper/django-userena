from django.db import models
from django.contrib.auth.models import User

from userena import settings as userena_settings
from userena.utils import generate_sha1

from guardian.shortcuts import assign

import re, datetime

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class AccountManager(models.Manager):
    """ Extra functionality for the account manager. """

    def create_inactive_user(self, username, email, password):
        """
        A simple wrapper that creates a new ``User`` and a new ``Account``.

        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        # Also create account.
        account = self.create_account(new_user)

        return new_user

    def create_account(self, user):
        """
        Create an ``Account`` for a given ``User``.

        The permissions of viewing, changing and deleting the account are
        granted to the user.

        Also creates a ``activation_key`` for this account. After the account
        is created an e-mail is send with ``send_activation_email`` to the
        user with this key.

        """
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        salt, activation_key = generate_sha1(username)
        account = self.create(user=user,
                              activation_key=activation_key,
                              activation_key_created=datetime.datetime.now())

        permissions = ['view_account', 'change_account', 'delete_account']
        for perm in permissions:
            assign(perm, account.user, account)

        account.send_activation_email()
        return account

    def activate_user(self, activation_key):
        """
        Activate an ``User`` by supplying a valid ``activation_key``.

        If the key is valid and an account is found, activate the user and
        return the account.

        """
        if SHA1_RE.search(activation_key):
            try:
                account = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not account.activation_key_expired():
                user = account.user
                user.is_active = True
                user.save()

                account.activation_key = userena_settings.USERENA_ACTIVATED
                account.save()
                return user
        return False

    def verify_email(self, verification_key):
        """
        Verify an email address by checking a ``verification_key``.

        A valid ``verification_key`` will set the newly wanted e-mail address
        as the current e-mail address. Returns the account after succes or
        ``False`` when the verification key is invalid.

        """
        if SHA1_RE.search(verification_key):
            try:
                account = self.get(email_verification_key=verification_key,
                                   email_new__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user = account.user
                user.email = account.email_new
                user.save()

                account.email_new, account.email_verification_key = '',''
                account.save()
                return account
        return False

    def delete_expired_users(self):
        """
        Checks for expired accounts and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        Returns a list of the deleted users.

        """
        deleted_users = []
        for account in self.filter(user__is_staff=False):
            if account.activation_key_expired():
                deleted_users.append(account.user)
                account.user.delete()
        return deleted_users
