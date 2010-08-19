from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings

from userena import forms
from userena.models import UserenaUser, Profile
from userena import settings as userena_settings

class UserenaViewsTests(TestCase):
    """ Test the account views """
    fixtures = ['users', 'profiles']

    def test_valid_activation(self):
        """ A ``GET`` to the activation view """
        # First, register an account.
        self.client.post(reverse('userena_signup'),
                         data={'username': 'alice',
                               'email': 'alice@example.com',
                               'password1': 'swordfish',
                               'password2': 'swordfish',
                               'tos': 'on'})
        user = UserenaUser.objects.get(user__email='alice@example.com')
        response = self.client.get(reverse('userena_activate',
                                           kwargs={'activation_key': user.activation_key}))
        self.assertRedirects(response,
                             reverse('userena_activation_complete'))

        user = UserenaUser.objects.get(email='alice@example.com')
        self.failUnless(user.is_active)

    def test_invalid_activation(self):
        """
        A ``GET`` to the activation view with a wrong ``activation_key``.

        """
        response = self.client.get(reverse('userena_activate',
                                           kwargs={'activation_key': 'fake'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userena/activation_fail.html')

    def test_valid_verification(self):
        """ A ``GET`` to the verification view """
        # First, try to change an email.
        user = UserenaUser.objects.get(pk=1)
        user.change_email('johnie@example.com')

        response = self.client.get(reverse('userena_verify',
                                           kwargs={'verification_key': user.email_verification_key}))

        self.assertRedirects(response,
                             reverse('userena_verification_complete'))

    def test_invalid_verification(self):
        """
        A ``GET`` to the verification view with an invalid verification key.

        """
        response = self.client.get(reverse('userena_verify',
                                           kwargs={'verification_key': 'WRONG'}))
        self.assertTemplateUsed(response,
                                'userena/verification_fail.html')

    def test_disabled_view(self):
        """ A ``GET`` to the ``disabled`` view """
        response = self.client.get(reverse('userena_disabled'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userena/disabled.html')

    def test_signup_view(self):
        """ A ``GET`` to the ``signup`` view """
        response = self.client.get(reverse('userena_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userena/signup_form.html')

        # Check that the correct form is used.
        self.failUnless(isinstance(response.context['form'],
                                   forms.SignupForm))

    def test_signup_view_success(self):
        """
        After a ``POST`` to the ``signup`` view a new user should be created,
        the user should be logged in and redirected to the signup success page.

        """
        response = self.client.post(reverse('userena_signup'),
                                    data={'username': 'alice',
                                          'email': 'alice@example.com',
                                          'password1': 'blueberry',
                                          'password2': 'blueberry',
                                          'tos': 'on'})

        # Check for redirect.
        self.assertRedirects(response,
                             reverse('userena_signup_complete'))

        # Check for new user.
        self.assertEqual(UserenaUser.objects.filter(email__iexact='alice@example.com').count(), 1)


    def test_signin_view(self):
        """ A ``GET`` to the signin view should render the correct form """
        response = self.client.get(reverse('userena_signin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userena/signin_form.html')

        # Check the correct form is used
        self.failUnless(isinstance(response.context['form'],
                                   forms.AuthenticationForm))

    def test_signin_view_remember_me_on(self):
        """
        A ``POST`` to the signin with tells it to remember the user for
        ``REMEMBER_ME_DAYS``.

        """
        response = self.client.post(reverse('userena_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish',
                                          'remember_me': True})
        self.assertEqual(self.client.session.get_expiry_age(),
                         userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 3600)

    def test_signin_view_remember_off(self):
        """
        A ``POST`` to the signin view of which the user doesn't want to be
        remembered.

        """
        response = self.client.post(reverse('userena_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish'})

        self.failUnless(self.client.session.get_expire_at_browser_close())

    def test_signin_view_inactive(self):
        """ A ``POST`` from a inactive user """
        user = User.objects.get(email='john@example.com')
        user.is_active = False
        user.save()

        response = self.client.post(reverse('userena_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish'})

        self.assertRedirects(response,
                             reverse('userena_disabled'))

    def test_signin_view_success(self):
        """
        A valid ``POST`` to the signin view should redirect the user to it's
        own account page if no ``next`` value is supplied. Else it should
        redirect to ``next``.

        """
        response = self.client.post(reverse('userena_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish'})

        self.assertRedirects(response, reverse('userena_profile_detail',
                                               kwargs={'username': 'john'}))

        # Redirect to supplied ``next`` value.
        response = self.client.post(reverse('userena_signin'),
                                    data={'identification': 'john@example.com',
                                          'password': 'blowfish',
                                          'next': '/accounts/'})
        self.assertRedirects(response, '/accounts/')

    def test_signout_view(self):
        """ A ``GET`` to the signout view """
        response = self.client.get(reverse('userena_signout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'userena/signout.html')

    def test_change_email_view(self):
        """ A ``GET`` to the change e-mail view. """
        response = self.client.get(reverse('userena_email_change',
                                           kwargs={'username': 'john'}))

        # Anonymous user should not be able to view the profile page
        self.assertRedirects(response,
                             reverse('userena_signin') + '?next=' + reverse('userena_email_change',
                                                                            kwargs={'username': 'john'}))

        # Login
        client = self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_email_change',
                                           kwargs={'username': 'john'}))

        self.assertEqual(response.status_code, 200)

        # Check that the correct form is used.
        self.failUnless(isinstance(response.context['form'],
                                   forms.ChangeEmailForm))

        self.assertTemplateUsed(response,
                                'userena/email_form.html')

    def test_change_valid_email_view(self):
        """ A ``POST`` with a valid e-mail address """
        self.client.login(username='john', password='blowfish')
        response = self.client.post(reverse('userena_email_change',
                                            kwargs={'username': 'john'}),
                                    data={'email': 'john_new@example.com'})

        self.assertRedirects(response,
                             reverse('userena_email_complete',
                                     kwargs={'username': 'john'}))

    def test_change_password_view(self):
        """ A ``GET`` to the change password view """
        self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_password_change',
                                           kwargs={'username': 'john'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userena/password_form.html')
        self.failUnless(response.context['form'],
                        PasswordChangeForm)

    def test_change_password_view_success(self):
        """ A valid ``POST`` to the password change view """
        self.client.login(username='john', password='blowfish')

        new_password = 'suckfish'
        response = self.client.post(reverse('userena_password_change',
                                            kwargs={'username': 'john'}),
                                    data={'new_password1': new_password,
                                          'new_password2': 'suckfish',
                                          'old_password': 'blowfish'})

        self.assertRedirects(response, reverse('userena_password_change_complete',
                                               kwargs={'username': 'john'}))

        # Check that the new password is set.
        john = User.objects.get(username='john')
        self.failUnless(john.check_password(new_password))

    def test_profile_detail_view(self):
        """ A ``GET`` to the detailed view of a user """
        response = self.client.get(reverse('userena_profile_detail',
                                           kwargs={'username': 'john'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userena/profile_detail.html')

    def test_profile_edit_view(self):
        """ A ``GET`` to the edit view of a users account """
        self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_profile_edit',
                                           kwargs={'username': 'john'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userena/profile_form.html')
        self.failUnless(isinstance(response.context['form'],
                                   forms.EditProfileForm))

    def test_profile_edit_view_success(self):
        """ A ``POST`` to the edit view """
        self.client.login(username='john', password='blowfish')
        new_about_me = 'I hate it when people use my name for testing.'
        response = self.client.post(reverse('userena_profile_edit',
                                            kwargs={'username': 'john'}),
                                    data={'about_me': new_about_me,
                                          'privacy': 'open'})

        # A valid post should redirect to the detail page.
        self.assertRedirects(response, reverse('userena_profile_detail',
                                               kwargs={'username': 'john'}))

        # Users hould be changed now.
        profile = UserenaUser.objects.get(username='john').get_profile()
        self.assertEqual(profile.about_me, new_about_me)


    def test_profile_list_view(self):
        """ A ``GET`` to the list view of a user """
        response = self.client.get(reverse('userena_profile_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userena/profile_list.html')
