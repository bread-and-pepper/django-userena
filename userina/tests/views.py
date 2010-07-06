from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail

from userina import forms
from userina.models import Account

class AccountViewsTests(TestCase):
    """ Test the account views """

    def test_signup_view(self):
        """ A ``GET`` to the ``signup`` view """
        response = self.client.get(reverse('userina_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userina/signup_form.html')

        # Check that the correct form is used.
        self.failUnless(isinstance(response.context['form'],
                                   forms.SignupForm))

    def test_signup_view_success(self):
        """
        After a ``POST`` to the ``signup`` view a new user should be created,
        the user should be logged in and redirected to the signup success page.

        """
        response = self.client.post(reverse('userina_signup'),
                                    data={'username': 'alice',
                                          'email': 'alice@example.com',
                                          'password1': 'blueberry',
                                          'password2': 'blueberry',
                                          'tos': 'on'})

        # Check for redirect.
        self.assertRedirects(response,
                             reverse('userina_signup_complete'))

        # Check for new user.
        self.assertEqual(Account.objects.get(user__email__iexact='alice@example.com').count(), 1)

        # User should be active (Django).
        user = User.objects.get(email__iexact='alice@example.com')
        self.assertEqual(user.is_active(), True)

        # User should not be verified (Userina).
        self.assertEqual(user.account.is_verified(), False)

        # User should be logged in.

        # User should have gotten a email.
        self.assertEqual(len(mail.outbox), 1)
