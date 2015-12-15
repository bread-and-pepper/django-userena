# encoding: utf-8
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _, override

from userena import forms
from userena import settings as userena_settings


class SignupFormTests(TestCase):
    """ Test the signup form. """
    fixtures = ['users']

    def test_signup_form(self):
        """
        Test that the ``SignupForm`` checks for unique usernames and unique
        e-mail addresses.

        """
        invalid_data_dicts = [
            # Non-alphanumeric username.
            {'data': {'username': 'foo@bar',
                      'email': 'foo@example.com',
                      'password': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [_('Username must contain only letters, numbers, dots and underscores.')])},
            # Password is not the same
            {'data': {'username': 'katy-',
                      'email': 'katy@newexample.com',
                      'password1': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('__all__', [_('The two password fields didn\'t match.')])},

            # Already taken username
            {'data': {'username': 'john',
                      'email': 'john@newexample.com',
                      'password1': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [_('This username is already taken.')])},

            # Forbidden username
            {'data': {'username': 'SignUp',
                      'email': 'foo@example.com',
                      'password': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('username', [_('This username is not allowed.')])},

            # Already taken email
            {'data': {'username': 'alice',
                      'email': 'john@example.com',
                      'password': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('email', [_('This email is already in use. Please supply a different email.')])},
        ]

        # Override locale settings since we are checking for existence of error
        # messaged written in english. Note: it should not be necessasy but
        # we have experienced such locale issues during tests on Travis builds.
        # See: https://github.com/bread-and-pepper/django-userena/issues/446
        with override('en'):
            for invalid_dict in invalid_data_dicts:
                form = forms.SignupForm(data=invalid_dict['data'])
                self.assertFalse(form.is_valid())
                self.assertEqual(form.errors[invalid_dict['error'][0]],
                                 invalid_dict['error'][1])

        # And finally, a valid form.
        form = forms.SignupForm(data={'username': 'foo.bla',
                                      'email': 'foo@example.com',
                                      'password1': 'foo',
                                      'password2': 'foo',
                                      'tos': 'on'})

        self.assertTrue(form.is_valid())


class AuthenticationFormTests(TestCase):
    """ Test the ``AuthenticationForm`` """

    fixtures = ['users',]

    def test_signin_form(self):
        """
        Check that the ``SigninForm`` requires both identification and password

        """
        invalid_data_dicts = [
            {'data': {'identification': '',
                      'password': 'inhalefish'},
             'error': ('identification', ['Either supply us with your email or username.'])},
            {'data': {'identification': 'john',
                      'password': 'inhalefish'},
             'error': ('__all__', ['Please enter a correct username or email and password. Note that both fields are case-sensitive.'])}
        ]

        # Override locale settings since we are checking for existence of error
        # messaged written in english. Note: it should not be necessasy but
        # we have experienced such locale issues during tests on Travis builds.
        # See: https://github.com/bread-and-pepper/django-userena/issues/446
        with override('en'):
            for invalid_dict in invalid_data_dicts:
                form = forms.AuthenticationForm(data=invalid_dict['data'])
                self.assertFalse(form.is_valid())
                self.assertEqual(form.errors[invalid_dict['error'][0]],
                                 invalid_dict['error'][1])

        valid_data_dicts = [
            {'identification': 'john',
             'password': 'blowfish'},
            {'identification': 'john@example.com',
             'password': 'blowfish'}
        ]

        for valid_dict in valid_data_dicts:
            form = forms.AuthenticationForm(valid_dict)
            self.assertTrue(form.is_valid())

    def test_signin_form_email(self):
        """
        Test that the signin form has a different label is
        ``USERENA_WITHOUT_USERNAME`` is set to ``True``

        """
        userena_settings.USERENA_WITHOUT_USERNAMES = True

        form = forms.AuthenticationForm(data={'identification': "john",
                                              'password': "blowfish"})

        correct_label = "Email"
        self.assertEqual(form.fields['identification'].label,
                         correct_label)

        # Restore default settings
        userena_settings.USERENA_WITHOUT_USERNAMES = False


class SignupFormOnlyEmailTests(TestCase):
    """
    Test the :class:`SignupFormOnlyEmail`.

    This is the same form as :class:`SignupForm` but doesn't require an
    username for a successfull signup.

    """
    fixtures = ['users']

    def test_signup_form_only_email(self):
        """
        Test that the form has no username field. And that the username is
        generated in the save method

        """
        valid_data = {'email': 'hans@gretel.com',
                      'password1': 'blowfish',
                      'password2': 'blowfish'}

        form = forms.SignupFormOnlyEmail(data=valid_data)

        # Should have no username field
        self.assertFalse(form.fields.get('username', False))

        # Form should be valid.
        self.assertTrue(form.is_valid())

        # Creates an unique username
        user = form.save()

        self.assertTrue(len(user.username), 5)


class ChangeEmailFormTests(TestCase):
    """ Test the ``ChangeEmailForm`` """
    fixtures = ['users']

    def test_change_email_form(self):
        user = get_user_model().objects.get(pk=1)
        invalid_data_dicts = [
            # No change in e-mail address
            {'data': {'email': 'john@example.com'},
             'error': ('email', ['You\'re already known under this email.'])},
            # An e-mail address used by another
            {'data': {'email': 'jane@example.com'},
             'error': ('email', ['This email is already in use. Please supply a different email.'])},
        ]

        # Override locale settings since we are checking for existence of error
        # messaged written in english. Note: it should not be necessasy but
        # we have experienced such locale issues during tests on Travis builds.
        # See: https://github.com/bread-and-pepper/django-userena/issues/446
        with override('en'):
            for invalid_dict in invalid_data_dicts:
                form = forms.ChangeEmailForm(user, data=invalid_dict['data'])
                self.assertFalse(form.is_valid())
                self.assertEqual(form.errors[invalid_dict['error'][0]],
                                 invalid_dict['error'][1])

        # Test a valid post
        form = forms.ChangeEmailForm(user,
                                     data={'email': 'john@newexample.com'})
        self.assertTrue(form.is_valid())

    def test_form_init(self):
        """ The form must be initialized with a ``User`` instance. """
        self.assertRaises(TypeError, forms.ChangeEmailForm, None)


class EditAccountFormTest(TestCase):
    """ Test the ``EditAccountForm`` """
    pass
