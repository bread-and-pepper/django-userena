import urllib, hashlib

def get_gravatar(email, size=80, default='identicon'):
    """ Get's a gravatar for a e-mail address.  """
    gravatar_url = 'http://www.gravatar.com/avatar/%(gravatar_id)s?' % \
            {'gravatar_id': hashlib.md5(email.lower()).hexdigest()}

    gravatar_url += urllib.urlencode({'s': str(size),
                                      'd': default})
    return gravatar_url
