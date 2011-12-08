from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail

from userena.admin import accept_signup, reject_signup
from userena.models import UserenaSignup
from userena import settings as userena_settings

class UserenaAdminTests(TestCase):
    """ Test the admin interface of userena """
    fixtures = ['users']

    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    def test_accept_signup(self):
        """ Test that the user passes moderation """
        new_user = UserenaSignup.objects.create_user(**self.user_info)
        queryset = User.objects.filter(username='alice')
        
        # Run the function
        accept_signup(User, None, queryset)

        # Test that the user is activated and got an email
        accepted_user = User.objects.get(username='alice')

        # User should be active
        self.failUnless(accepted_user.is_active)

        # User should have received two e-mails. One for activation, one for
        # being accepted.
        self.failUnlessEqual(len(mail.outbox), 2)

        # Key should be the activated key from settings
        self.failUnlessEqual(accepted_user.userena_signup.activation_key,
                             userena_settings.USERENA_ACTIVATED)

    def test_reject_signup(self):
        """ Test that the user is rejected """
        new_user = UserenaSignup.objects.create_user(**self.user_info)
        queryset = User.objects.filter(username='alice')
        
        # Run the function
        reject_signup(User, None, queryset)

        # Test the rejection
        rejected_user = User.objects.get(username='alice')
        
        # User shouldn't be active
        self.failIf(rejected_user.is_active)

        # User should have received two e-mails. One for activation, one for
        # being accepted.
        self.failUnlessEqual(len(mail.outbox), 2)
        
        # Key should be the rejection key
        self.failUnlessEqual(rejected_user.userena_signup.activation_key,
                             userena_settings.USERENA_ACTIVATION_REJECTED)
