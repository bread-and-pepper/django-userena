from django.db import models
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor

from userena import settings as userena_settings

import re, datetime, random

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

        # Create account also
        account = self.create_account(new_user)

        return new_user

    def create_account(self, user):
        """
        Create an ``Account`` for a given ``User``.

        Also creates a ``activation_key`` for this account. After the account
        is created an e-mail is send with ``send_activation_email`` to the
        user with this key.

        """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        activation_key = sha_constructor(salt+username).hexdigest()
        account = self.create(user=user,
                              activation_key=activation_key,
                              activation_key_created=datetime.datetime.now())
        account.send_activation_email()
        return account

    def activate_user(self, activation_key):
        """
        Activate an ``Account`` by supplying a valid ``activation_key``.

        If the key is valid and an account is found, activate the user and
        return the activied account.

        """
        if SHA1_RE.search(activation_key):
            try:
                account = self.get(activation_key=activation_key)
            except self.Model.DoesNotExist:
                return False
            if not account.activation_key_expired():
                user = account.user
                user.is_active = True
                user.save()

                account.activation_key = userena_settings.USERENA_ACTIVATED
                account.save()
                return account
        return False

    def notify_almost_expired(self):
        """
        Check for accounts that are ``USERENA_ACTIVATED_NOTIFY_DAYS`` days
        before expiration. For each account that's found
        ``send_expiry_notification`` is called.

        Returns a list of all the accounts that have received a notification.

        """
        if userena_settings.USERENA_ACTIVATION_NOTIFY:
            expiration_date = datetime.datetime.now() - datetime.timedelta(days=(userena_settings.USERENA_ACTIVATION_DAYS - userena_settings.USERENA_ACTIVATION_NOTIFY_DAYS))

            accounts = self.filter(user__is_active=False,
                                   user__is_staff=False,
                                   activation_notification_send=False)
            notified_accounts = []
            for account in accounts:
                if account.activation_key_almost_expired():
                    account.send_expiry_notification()
                    notified_accounts.append(account)
            return notified_accounts

    def delete_expired_users(self):
        """
        Checks for expired accounts and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        Returns a list of the deleted accounts.

        """
        deleted_users = []
        for account in self.filter(user__is_staff=False):
            if account.activation_key_expired():
                deleted_users.append(account.user)
                account.user.delete()
        return deleted_users
