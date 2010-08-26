from django.db import models
from django.db.models import Q
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AnonymousUser

from userena import settings as userena_settings
from userena.utils import generate_sha1, get_profile_model

from guardian.shortcuts import assign

import re, datetime

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class UserenaUserManager(UserManager):
    """ Extra functionality for the UserenaUser model. """

    def create_inactive_user(self, username, email, password):
        """
        A simple wrapper that creates a new ``User``.

        """
        now = datetime.datetime.now()

        new_user = self.model(username=username, email=email, is_staff=False,
                              is_active=False, is_superuser=False, last_login=now,
                              date_joined=now)

        new_user.set_password(password)

        # Create activation key
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        salt, activation_key = generate_sha1(username)

        new_user.activation_key = activation_key
        new_user.activation_key_created = datetime.datetime.now()

        new_user.save(using=self._db)

        # All users have an empty profile
        profile_model = get_profile_model()
        new_profile = profile_model(user=new_user)
        new_profile.save(using=self._db)

        # Give permissions to view and change profile
        permissions = ['view_profile', 'change_profile']
        for perm in permissions:
            assign(perm, new_user.user, new_profile)

        new_user.send_activation_email()

        return new_user

    def activate_user(self, activation_key):
        """
        Activate an ``User`` by supplying a valid ``activation_key``.

        If the key is valid and an user is found, activate the user and
        return it.

        """
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.is_active = True
                user.activation_key = userena_settings.USERENA_ACTIVATED
                user.save(using=self._db)
                return user
        return False

    def verify_email(self, verification_key):
        """
        Verify an email address by checking a ``verification_key``.

        A valid ``verification_key`` will set the newly wanted e-mail address
        as the current e-mail address. Returns the user after success or
        ``False`` when the verification key is invalid.

        """
        if SHA1_RE.search(verification_key):
            try:
                user = self.get(email_verification_key=verification_key,
                                email_new__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user.email = user.email_new
                user.email_new, user.email_verification_key = '',''
                user.save(using=self._db)
                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        Returns a list of the deleted users.

        """
        deleted_users = []
        for user in self.filter(is_staff=False):
            if user.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users

class UserenaBaseProfileManager(models.Manager):
    """ Manager for UserenaProfile """
    def get_visible_profiles(self, user=None):
        """
        Returns all the visible profiles available to this user.

        For now keeps it simple by just applying the cases when a user is not
        active, a user has it's profile closed to everyone or a user only
        allows registered users to view their profile.

        **Keyword Arguments**

        ``user``
            A django ``User`` instance.

        """
        profiles = self.all()

        filter_kwargs = {'user__is_active': True}

        profiles = profiles.filter(**filter_kwargs)
        if user and isinstance(user, AnonymousUser):
            profiles = profiles.exclude(Q(privacy='closed') | Q(privacy='registered'))
        else: profiles = profiles.exclude(Q(privacy='closed'))
        return profiles
