from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, UserManager, Permission, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from userena import settings as userena_settings
from userena.utils import generate_sha1, get_profile_model
from userena import signals as userena_signals

from guardian.shortcuts import assign, get_perms

import re, datetime

SHA1_RE = re.compile('^[a-f0-9]{40}$')

ASSIGNED_PERMISSIONS = {
    'profile':
        (('view_profile', 'Can view profile'),
         ('change_profile', 'Can change profile'),
         ('delete_profile', 'Can delete profile')),
    'user':
        (('change_user', 'Can change user'),
         ('delete_user', 'Can delete user'))
}

class UserenaManager(UserManager):
    """ Extra functionality for the Userena model. """

    def create_user(self, username, email, password, active=False,
                    send_email=True):
        """
        A simple wrapper that creates a new :class:`User`.

        :param username:
            String containing the username of the new user.

        :param email:
            String containing the email address of the new user.

        :param password:
            String containing the password for the new user.

        :param active:
            Boolean that defines if the user requires activation by clicking 
            on a link in an e-mail. Defauts to ``True``.

        :param send_email:
            Boolean that defines if the user should be send an email. You could
            set this to ``False`` when you want to create a user in your own
            code, but don't want the user to activate through email.

        :return: :class:`User` instance representing the new user.

        """
        now = datetime.datetime.now()

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = active
        new_user.save()

        userena_profile = self.create_userena_profile(new_user)

        # All users have an empty profile
        profile_model = get_profile_model()
        try:
            new_profile = new_user.get_profile()
        except profile_model.DoesNotExist:
            new_profile = profile_model(user=new_user)
            new_profile.save(using=self._db)

        # Give permissions to view and change profile
        for perm in ASSIGNED_PERMISSIONS['profile']:
            assign(perm[0], new_user, new_profile)

        # Give permissions to view and change itself
        for perm in ASSIGNED_PERMISSIONS['user']:
            assign(perm[0], new_user, new_user)

        if send_email:
            userena_profile.send_activation_email()

        # Send the signup complete signal
        userena_signals.signup_complete.send(sender=None,
                                             user=new_user)

        return new_user

    def create_userena_profile(self, user):
        """
        Creates an :class:`UserenaSignup` instance for this user.

        :param user:
            Django :class:`User` instance.

        :return: The newly created :class:`UserenaSignup` instance.

        """
        if isinstance(user.username, unicode):
            user.username = user.username.encode('utf-8')
        salt, activation_key = generate_sha1(user.username)

        return self.create(user=user,
                           activation_key=activation_key)

    def activate_user(self, username, activation_key):
        """
        Activate an :class:`User` by supplying a valid ``activation_key``.

        If the key is valid and an user is found, activates the user and
        return it. Also sends the ``activation_complete`` signal.

        :param username:
            String containing the username that wants to be activated.

        :param activation_key:
            String containing the secret SHA1 for a valid activation.

        :return:
            The newly activated :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(activation_key):
            try:
                userena = self.get(user__username=username,
                                   activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not userena.activation_key_expired():
                userena.activation_key = userena_settings.USERENA_ACTIVATED
                user = userena.user
                user.is_active = True
                userena.save(using=self._db)
                user.save(using=self._db)

                # Send the activation_complete signal
                userena_signals.activation_complete.send(sender=None,
                                                         user=user)

                return user
        return False

    def confirm_email(self, username, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted e-mail address
        as the current e-mail address. Returns the user after success or
        ``False`` when the confirmation key is invalid.

        :param username:
            String containing the username of the user that wants their email
            verified.

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                userena = self.get(user__username=username,
                                   email_confirmation_key=confirmation_key,
                                   email_unconfirmed__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user = userena.user
                user.email = userena.email_unconfirmed
                userena.email_unconfirmed, userena.email_confirmation_key = '',''
                userena.save(using=self._db)
                user.save(using=self._db)

                # Send the activation_complete signal
                userena_signals.confirmation_complete.send(sender=None,
                                                           user=user)

                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.

        """
        deleted_users = []
        for user in User.objects.filter(is_staff=False,
                                        is_active=False):
            if user.userena_signup.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users

    def check_permissions(self):
        """
        Checks that all permissions are set correctly for the users.

        :return: A set of users whose permissions was wrong.

        """
        # Variable to supply some feedback
        changed_permissions = []
        changed_users = []
        warnings = []

        # Check that all the permissions are available.
        for model, perms in ASSIGNED_PERMISSIONS.items():
            if model == 'profile':
                model_obj = get_profile_model()
            else: model_obj = User
            model_content_type = ContentType.objects.get_for_model(model_obj)
            for perm in perms:
                try:
                    Permission.objects.get(codename=perm[0],
                                           content_type=model_content_type)
                except Permission.DoesNotExist:
                    changed_permissions.append(perm[1])
                    Permission.objects.create(name=perm[1],
                                              codename=perm[0],
                                              content_type=model_content_type)

        for user in User.objects.all():
            if not user.username == 'AnonymousUser':
                try:
                    user_profile = user.get_profile()
                except get_profile_model().DoesNotExist:
                    warnings.append(_("No profile found for %(username)s") \
                                        % {'username': user.username})
                else:
                    all_permissions = get_perms(user, user_profile) + get_perms(user, user)

                    for model, perms in ASSIGNED_PERMISSIONS.items():
                        if model == 'profile':
                            perm_object = user.get_profile()
                        else: perm_object = user

                        for perm in perms:
                            if perm[0] not in all_permissions:
                                assign(perm[0], user, perm_object)
                                changed_users.append(user)

        return (changed_permissions, changed_users, warnings)

class UserenaBaseProfileManager(models.Manager):
    """ Manager for :class:`UserenaProfile` """
    def get_visible_profiles(self, user=None):
        """
        Returns all the visible profiles available to this user.

        For now keeps it simple by just applying the cases when a user is not
        active, a user has it's profile closed to everyone or a user only
        allows registered users to view their profile.

        :param user:
            A Django :class:`User` instance.

        :return:
            All profiles that are visible to this user.

        """
        profiles = self.all()

        filter_kwargs = {'user__is_active': True}

        profiles = profiles.filter(**filter_kwargs)
        if user and isinstance(user, AnonymousUser):
            profiles = profiles.exclude(Q(privacy='closed') | Q(privacy='registered'))
        else: profiles = profiles.exclude(Q(privacy='closed'))
        return profiles
