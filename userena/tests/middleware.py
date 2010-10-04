from django.http import HttpRequest
from django.utils.importlib import import_module
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from userena.tests.profiles.test import ProfileTestCase
from userena.tests.profiles.models import Profile
from userena.middleware import UserenaLocaleMiddleware
from userena import settings as userena_settings

class UserenaLocaleMiddlewareTests(ProfileTestCase):
    """ Test the ``UserenaLocaleMiddleware`` """
    fixtures = ['users', 'profiles']

    def _get_request_with_user(self, user):
        """ Fake a request with an user """
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
        }
        request.method = 'GET'
        request.session = {}

        # Add user
        request.user = user
        return request

    def test_preference_user(self):
        """ Test the language preference of two users """
        users = ((1, 'nl'),
                 (2, 'en'))

        for pk, lang in users:
            user = User.objects.get(pk=pk)
            profile = user.get_profile()

            req = self._get_request_with_user(user)

            # Check that the user has this preference
            self.failUnlessEqual(profile.language, lang)

            # Request should have a ``LANGUAGE_CODE`` with dutch
            UserenaLocaleMiddleware().process_request(req)
            self.failUnlessEqual(req.LANGUAGE_CODE, lang)

    def test_without_profile(self):
        """ Middleware should do nothing when a user has no profile """
        # Delete the profile
        Profile.objects.get(pk=1).delete()
        user = User.objects.get(pk=1)

        # User shouldn't have a profile
        self.assertRaises(ObjectDoesNotExist, user.get_profile)

        req = self._get_request_with_user(user)
        UserenaLocaleMiddleware().process_request(req)

        self.failIf(hasattr(req, 'LANGUAGE_CODE'))

    def test_without_language_field(self):
        """ Middleware should do nothing if the profile has no language field """
        userena_settings.USERENA_LANGUAGE_FIELD = 'non_existant_language_field'
        user = User.objects.get(pk=1)

        req = self._get_request_with_user(user)

        # Middleware should do nothing
        UserenaLocaleMiddleware().process_request(req)
        self.failIf(hasattr(req, 'LANGUAGE_CODE'))
