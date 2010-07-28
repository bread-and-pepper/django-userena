from django.conf import settings
from userena import settings as userena_settings

import urllib, hashlib

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

    ** Keyword Arguments **

    ``redirect``
        A value normally supplied by ``next`` form field. Get's preference
        before the default view which requires the user.

    ``user``
        A ``User`` object specifying the user who has just signed in.

    """
    if redirect: return redirect
    elif user:
        return settings.LOGIN_REDIRECT_URL % \
                {'username': user.username}
    else:
        return settings.LOGIN_REDIRECT_URL
