from django.core.validators import email_re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings as django_settings

# Check if ``dateutils`` and ``easy_thumbnails`` is installed.
try:
    import dateutil
except ImportError:
    raise ImproperlyConfigured('You need the dateutils application to use django-userina')

if not 'easy_thumbnails' in django_settings.INSTALLED_APPS:
    raise ImproperlyConfigured('You need the easy_thumbnails application to use django-userina.')

class UserinaAuthenticationBackend(ModelBackend):
    """
    We use a custom backend because we want the user to be able to supply a
    ``email`` or ``username`` to the login form. We will find out what they
    supplied here.

    """
    def authenticate(self, identification, password=None):
        if email_re.search(identification):
            try:
                user = User.objects.get(email=identification)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username=identification)
            except User.DoesNotExist:
                return None
        return user if user.check_password(password) else None
