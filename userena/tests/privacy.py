from django.core.urlresolvers import reverse

from userena.tests.profiles.test import ProfileTestCase
from userena.tests.profiles.models import Profile

class PrivacyTests(ProfileTestCase):
    """
    Privacy testing of views concerning profiles.

    Test the privacy of the views that are available with three type of users:

        - Anonymous: An user that is not signed in.
        - Registered: An user that is registered and signed in.
        - Superuser: An user that is administrator at the site.

    """
    fixtures = ['users', 'profiles']

    reg_user = {'username': 'jane',
                'password': 'blowfish'}

    super_user = {'username': 'john',
                  'password': 'blowfish'}

    detail_profile_url = reverse('userena_profile_detail',
                                 kwargs={'username': 'john'})

    edit_profile_url = reverse('userena_profile_edit',
                                kwargs={'username': 'john'})

    def _test_status_codes(self, url, users_status):
        """
        Test if the status codes are corresponding to what that user should
        see.

        """
        for user, status in users_status:
            if user:
                self.client.login(**user)
            response = self.client.get(url)
            self.failUnlessEqual(response.status_code, status)

    def test_detail_open_profile_view(self):
        """ Viewing an open profile should be visible to everyone """
        profile = Profile.objects.get(pk=1)
        profile.privacy = 'open'
        profile.save()

        users_status = (
            (None, 200),
            (self.reg_user, 200),
            (self.super_user, 200)
        )
        self._test_status_codes(self.detail_profile_url, users_status)

    def test_detail_registered_profile_view(self):
        """ Viewing a users who's privacy is registered """
        profile = Profile.objects.get(pk=1)
        profile.privacy = 'registered'
        profile.save()

        users_status = (
            (None, 403),
            (self.reg_user, 200),
            (self.super_user, 200)
        )
        self._test_status_codes(self.detail_profile_url, users_status)

    def test_detail_closed_profile_view(self):
        """ Viewing a closed profile should only by visible to the admin """
        profile = Profile.objects.get(pk=1)
        profile.privacy = 'closed'
        profile.save()

        users_status = (
            (None, 403),
            (self.reg_user, 403),
            (self.super_user, 200)
        )
        self._test_status_codes(self.detail_profile_url, users_status)

    def test_edit_profile_view(self):
        """ Editing a profile should only be available to the owner and the admin """
        profile = Profile.objects.get(pk=1)

        users_status = (
            (None, 403),
            (self.reg_user, 403),
            (self.super_user, 200)
        )
        self._test_status_codes(self.edit_profile_url, users_status)
