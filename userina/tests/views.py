from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth.models import User
from django.conf import settings

from userina import forms
from userina.models import Account
from userina import settings as userina_settings

class AccountViewsTests(TestCase):
    """ Test the account views """
    fixtures = ['users']

    def test_disabled_view(self):
        """ A ``GET`` to the ``disabled`` view """
        response = self.client.get(reverse('userina_disabled'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userina/disabled.html')

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
        self.assertEqual(Account.objects.filter(user__email__iexact='alice@example.com').count(), 1)


    def test_signin_view(self):
        """ A ``GET`` to the signin view should render the correct form """
        response = self.client.get(reverse('userina_signin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userina/signin_form.html')

        # Check the correct form is used
        self.failUnless(isinstance(response.context['form'],
                                   forms.AuthenticationForm))

    def test_signin_view_remember_on(self):
        """
        A ``POST`` to the signin with tells it to remember the user for
        ``REMEMBER_ME_ DAYS``.

        """
        response = self.client.post(reverse('userina_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish',
                                          'remember_me': 'on'})
        self.assertEqual(self.client.session.get_expiry_age(),
                         userina_settings.USERINA_REMEMBER_ME_DAYS[1] * 3600)

    def test_signin_view_remember_on(self):
        """
        A ``POST`` to the signin view of which the user doesn't want to be
        remembered.

        """
        response = self.client.post(reverse('userina_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish'})

        self.failUnless(self.client.session.get_expire_at_browser_close())

    def test_signin_view_inactive(self):
        """ A ``POST`` from a inactive user """
        user = User.objects.get(email='john@example.com')
        user.is_active = False
        user.save()

        response = self.client.post(reverse('userina_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish'})

        self.assertRedirects(response,
                             reverse('userina_disabled'))

    def test_signin_view_succes(self):
        """ A ``POST`` to the signin view should redirect the user. """
        response = self.client.post(reverse('userina_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish'})

        # Check for redirect
        self.assertRedirects(response,
                             settings.LOGIN_REDIRECT_URL)

    def test_signout_view(self):
        """ A ``GET`` to the signout view """
        response = self.client.get(reverse('userina_signout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userina/signout.html')

    def test_valid_verification(self):
        """ A ``GET`` to the verification view """
        # First, register an account.
        self.client.post(reverse('userina_signup'),
                         data={'username': 'alice',
                               'email': 'alice@example.com',
                               'password1': 'swordfish',
                               'password2': 'swordfish',
                               'tos': 'on'})
        account = Account.objects.get(user__email='alice@example.com')
        response = self.client.get(reverse('userina_verify',
                                           kwargs={'verification_key': account.verification_key}))
        self.assertRedirects(response,
                             reverse('userina_verification_complete'))

        account = Account.objects.get(user__email='alice@example.com')
        self.failUnless(account.is_verified)


    def test_invalid_verification(self):
        """
        A ``GET`` to the verification view with a wrong ``verification_key``.

        """
        response = self.client.get(reverse('userina_verify',
                                           kwargs={'verification_key': 'fake'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userina/verification.html')

    def test_profile_view(self):
        """ A ``GET`` to a profile page. """
        response = self.client.get(reverse('userina_me'))

        # Anonymous user should not be able to view the profile page
        self.assertRedirects(response,
                             reverse('userina_signin') + '?next=' + reverse('userina_me'))

        # John should
        self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userina_me'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userina/me.html')

    def test_change_email_view(self):
        """ A ``GET`` to the change e-mail view. """
        response = self.client.get(reverse('userina_email_change'))

        # Anonymous user should not be able to view the profile page
        self.assertRedirects(response,
                             reverse('userina_signin') + '?next=' + reverse('userina_email_change'))

        # Login
        self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userina_email_change'))

        self.assertEqual(response.status_code, 200)

        # Check that the correct form is used.
        self.failUnless(isinstance(response.context['form'],
                                   forms.ChangeEmailForm))

        self.assertTemplateUsed(response,
                                'userina/me_email_form.html')

    def test_change_valid_email_view(self):
        """ A ``POST`` with a valid e-mail address """
        response = self.client.post(reverse('userina_email_change'),
                                    data={'email': 'jane@example.com'})

