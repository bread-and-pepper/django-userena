from django.test import TestCase

from userina import forms

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

            # Already taken username
            {'data': {'username': 'john',
                      'email': 'john@newexample.com',
                      'password1': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [u'This username is already taken.'])},

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
