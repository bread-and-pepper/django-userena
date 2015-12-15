from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from userena.tests.profiles.models import Profile
from userena.middleware import UserenaLocaleMiddleware
from userena import settings as userena_settings
from userena.utils import get_user_profile, get_profile_model

User = get_user_model()


def has_profile(user):
    """Test utility function to check if user has profile"""
    profile_model = get_profile_model()
    try:
        profile = user.get_profile()
    except AttributeError:
        related_name = profile_model._meta.get_field('user')\
                                    .related_query_name()
        profile = getattr(user, related_name, None)
    except profile_model.DoesNotExist:
        profile = None

    return bool(profile)



class UserenaLocaleMiddlewareTests(TestCase):
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
            profile = get_user_profile(user=user)

            req = self._get_request_with_user(user)

            # Check that the user has this preference
            self.assertEqual(profile.language, lang)

            # Request should have a ``LANGUAGE_CODE`` with dutch
            UserenaLocaleMiddleware().process_request(req)
            self.assertEqual(req.LANGUAGE_CODE, lang)

    def test_without_profile(self):
        """ Middleware should do nothing when a user has no profile """
        # Delete the profile
        Profile.objects.get(pk=1).delete()
        user = User.objects.get(pk=1)

        # User shouldn't have a profile
        self.assertFalse(has_profile(user))

        req = self._get_request_with_user(user)
        UserenaLocaleMiddleware().process_request(req)

        self.assertFalse(hasattr(req, 'LANGUAGE_CODE'))

    def test_without_language_field(self):
        """ Middleware should do nothing if the profile has no language field """
        userena_settings.USERENA_LANGUAGE_FIELD = 'non_existant_language_field'
        user = User.objects.get(pk=1)

        req = self._get_request_with_user(user)

        # Middleware should do nothing
        UserenaLocaleMiddleware().process_request(req)
        self.assertFalse(hasattr(req, 'LANGUAGE_CODE'))
