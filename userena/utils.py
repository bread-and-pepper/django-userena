from django.conf import settings
from django.utils.hashcompat import sha_constructor
from django.contrib.auth.models import SiteProfileNotAvailable
from django.db.models import get_model

from userena import settings as userena_settings

import urllib, hashlib, random

def get_gravatar(email, size=80, default='identicon'):
    """ Get's a gravatar for a e-mail address.

    **Arguments**

    ``size``
        The size in pixels of one side of the gravatar's square image.
        Optional, if not supplied will default to ``80``.

    ``default``
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

    """
    if userena_settings.USERENA_USE_HTTPS:
        base_url = 'https://secure.gravatar.com/avatar/'
    else: base_url = 'http://www.gravatar.com/avatar/'

    gravatar_url = '%(base_url)s%(gravatar_id)s?' % \
            {'base_url': base_url,
             'gravatar_id': hashlib.md5(email.lower()).hexdigest()}

    gravatar_url += urllib.urlencode({'s': str(size),
                                      'd': default})
    return gravatar_url

def signin_redirect(redirect=None, user=None):
    """
    Redirect user after successfull signin.

    First looks for a ``requested_redirect``. If not supplied will fallback to
    the user specific account page. If all fails, will fallback to the standard
    Django ``LOGIN_REDIRECT_URL`` setting. Returns a string defining the URI to
    go next.

    **Keyword Arguments**

    ``redirect``
        A value normally supplied by ``next`` form field. Get's preference
        before the default view which requires the user.

    ``user``
        A ``User`` object specifying the user who has just signed in.

    """
    if redirect: return redirect
    elif user: return user.get_absolute_url()
    else: return settings.LOGIN_REDIRECT_URL

def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    Returns a tuple containing the salt and hash.

    **Arguments**

    ``string``
        The string that needs to be encrypted.

    **Keyword arguments**

    ``salt``
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    """
    if not salt:
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt+str(string)).hexdigest()

    return (salt, hash)

def get_profile_model():
    """
    Return the model class for the currently-active user profile
    model, as defined by the ``AUTH_PROFILE_MODULE`` setting.

    """
    if (not hasattr(settings, 'AUTH_PROFILE_MODULE')) or \
           (not settings.AUTH_PROFILE_MODULE):
        raise SiteProfileNotAvailable

    profile_mod = get_model(*settings.AUTH_PROFILE_MODULE.split('.'))
    if profile_mod is None:
        raise SiteProfileNotAvailable
    return profile_mod
