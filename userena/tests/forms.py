from django.test import TestCase
from django.contrib.auth.models import User

from userena import forms

class SignupFormTests(TestCase):
    """ Test the signup form. """
    fixtures = ['users', 'accounts']
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
             'error': ('username', [u'Username must contain only letters, numbers and underscores.'])},
            # Password is not the same
            {'data': {'username': 'katy',
                      'email': 'katy@newexample.com',
                      'password1': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('__all__', [u'The two password fields didn\'t match.'])},

            # Already taken username
            {'data': {'username': 'john',
                      'email': 'john@newexample.com',
                      'password1': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [u'This username is already taken.'])},

            # Forbidden username
            {'data': {'username': 'SignUp',
                      'email': 'foo@example.com',
                      'password': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('username', [u'This username is not allowed.'])},

            # Already taken email
            {'data': {'username': 'alice',
                      'email': 'john@example.com',
                      'password': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('email', [u'This email address is already in use. Please supply a different email address.'])},
        ]

        for invalid_dict in invalid_data_dicts:
            form = forms.SignupForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])


        # And finally, a valid form.
        form = forms.SignupForm(data={'username': 'foo',
                                      'email': 'foo@example.com',
                                      'password1': 'foo',
                                      'password2': 'foo',
                                      'tos': 'on'})

        self.failUnless(form.is_valid())

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
             'error': ('identification', [u'Either supply us with your e-mail address or username.'])},
            {'data': {'identification': 'john',
                      'password': 'inhalefish'},
             'error': ('__all__', [u'Please enter a correct username or email and password. Note that both fields are case-sensitive.'])}
        ]

        for invalid_dict in invalid_data_dicts:
            form = forms.AuthenticationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
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
            self.failUnless(form.is_valid())

class ChangeEmailFormTests(TestCase):
    """ Test the ``ChangeEmailForm`` """
    fixtures = ['users']
    def test_change_email_form(self):
        user = User.objects.get(email__iexact='john@example.com')
        invalid_data_dicts = [
            # No change in e-mail address
            {'data': {'email': 'john@example.com'},
             'error': ('email', [u'Your already known under this email address.'])},
            # An e-mail address used by another
            {'data': {'email': 'jane@example.com'},
             'error': ('email', [u'This email address is already in use. Please supply a different email address.'])},
        ]
        for invalid_dict in invalid_data_dicts:
            form = forms.ChangeEmailForm(user, data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

        # Test a valid post
        form = forms.ChangeEmailForm(user,
                                     data={'email': 'john@newexample.com'})
        self.failUnless(form.is_valid())

    def test_form_init(self):
        """ The form must be initialized with a ``User`` instance. """
        self.assertRaises(TypeError, forms.ChangeEmailForm, None)

class EditAccountFormTest(TestCase):
    """ Test the ``EditAccountForm`` """
