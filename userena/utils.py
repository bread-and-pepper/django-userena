from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable
from django.db.models import get_model

try:
    from hashlib import sha1 as sha_constructor, md5 as md5_constructor
except ImportError:
    from django.utils.hashcompat import sha_constructor, md5_constructor

from userena import settings as userena_settings

import urllib, random, datetime

try:
    from django.utils.text import truncate_words
except ImportError:
    # Django >=1.5
    from django.utils.text import Truncator
    from django.utils.functional import allow_lazy
    def truncate_words(s, num, end_text='...'):
        truncate = end_text and ' %s' % end_text or ''
        return Truncator(s).words(num, truncate=truncate)
    truncate_words = allow_lazy(truncate_words, unicode)

def get_gravatar(email, size=80, default='identicon'):
    """ Get's a Gravatar for a email address.

    :param size:
        The size in pixels of one side of the Gravatar's square image.
        Optional, if not supplied will default to ``80``.

    :param default:
        Defines what should be displayed if no image is found for this user.
        Optional argument which defaults to ``identicon``. The argument can be
        a URI to an image or one of the following options:

            ``404``
                Do not load any image if none is associated with the email
                hash, instead return an HTTP 404 (File Not Found) response.

            ``mm``
                Mystery-man, a simple, cartoon-style silhouetted outline of a
                person (does not vary by email hash).

            ``identicon``
                A geometric pattern based on an email hash.

            ``monsterid``
                A generated 'monster' with different colors, faces, etc.

            ``wavatar``
                Generated faces with differing features and backgrounds

    :return: The URI pointing to the Gravatar.

    """
    if userena_settings.USERENA_MUGSHOT_GRAVATAR_SECURE:
        base_url = 'https://secure.gravatar.com/avatar/'
    else: base_url = '//www.gravatar.com/avatar/'

    gravatar_url = '%(base_url)s%(gravatar_id)s?' % \
            {'base_url': base_url,
             'gravatar_id': md5_constructor(email.lower()).hexdigest()}

    gravatar_url += urllib.urlencode({'s': str(size),
                                      'd': default})
    return gravatar_url

def signin_redirect(redirect=None, user=None):
    """
    Redirect user after successful sign in.

    First looks for a ``requested_redirect``. If not supplied will fall-back to
    the user specific account page. If all fails, will fall-back to the standard
    Django ``LOGIN_REDIRECT_URL`` setting. Returns a string defining the URI to
    go next.

    :param redirect:
        A value normally supplied by ``next`` form field. Gets preference
        before the default view which requires the user.

    :param user:
        A ``User`` object specifying the user who has just signed in.

    :return: String containing the URI to redirect to.

    """
    if redirect: return redirect
    elif user is not None:
        return userena_settings.USERENA_SIGNIN_REDIRECT_URL % \
                {'username': user.username}
    else: return settings.LOGIN_REDIRECT_URL

def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not isinstance(string, (str, unicode)):
        string = str(string)
    if isinstance(string, unicode):
        string = string.encode("utf-8")
    if not salt:
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt+string).hexdigest()

    return (salt, hash)

def get_profile_model():
    """
    Return the model class for the currently-active user profile
    model, as defined by the ``AUTH_PROFILE_MODULE`` setting.

    :return: The model that is used as profile.

    """
    if (not hasattr(settings, 'AUTH_PROFILE_MODULE')) or \
           (not settings.AUTH_PROFILE_MODULE):
        raise SiteProfileNotAvailable

    profile_mod = get_model(*settings.AUTH_PROFILE_MODULE.rsplit('.',1))
    if profile_mod is None:
        raise SiteProfileNotAvailable
    return profile_mod

def get_protocol():
    """
    Returns a string with the current protocol.

    This can be either 'http' or 'https' depending on ``USERENA_USE_HTTPS``
    setting.

    """
    protocol = 'http'
    if userena_settings.USERENA_USE_HTTPS:
        protocol = 'https'
    return protocol

def get_datetime_now():
    """
    Returns datetime object with current point in time.

    In Django 1.4+ it uses Django's django.utils.timezone.now() which returns
    an aware or naive datetime that represents the current point in time
    when ``USE_TZ`` in project's settings is True or False respectively.
    In older versions of Django it uses datetime.datetime.now().

    """
    try:
        from django.utils import timezone
        return timezone.now() # pragma: no cover
    except ImportError: # pragma: no cover
        return datetime.datetime.now()

# Django 1.5 compatibility utilities, providing support for custom User models.
# Since get_user_model() causes a circular import if called when app models are
# being loaded, the user_model_label should be used when possible, with calls
# to get_user_model deferred to execution time

user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User
