# Userena settings file.
#
# Please consult the docs for more information about each setting.

from django.conf import settings
gettext = lambda s: s


USERENA_REDIRECT_ON_SIGNOUT = getattr(settings,
                                      'USERENA_REDIRECT_ON_SIGNOUT',
                                      None)

USERENA_SIGNIN_REDIRECT_URL = getattr(settings,
                                      'USERENA_SIGNIN_REDIRECT_URL',
                                      '/accounts/%(username)s/')

USERENA_ACTIVATION_REQUIRED = getattr(settings,
                                      'USERENA_ACTIVATION_REQUIRED',
                                      True)

USERENA_ACTIVATION_DAYS = getattr(settings,
                                  'USERENA_ACTIVATION_DAYS',
                                  7)

USERENA_ACTIVATION_NOTIFY = getattr(settings,
                                    'USERENA_ACTIVATION_NOTIFY',
                                    True)

USERENA_ACTIVATION_NOTIFY_DAYS = getattr(settings,
                                         'USERENA_ACTIVATION_NOTIFY_DAYS',
                                         5)

USERENA_ACTIVATED = getattr(settings,
                            'USERENA_ACTIVATED',
                            'ALREADY_ACTIVATED')

USERENA_REMEMBER_ME_DAYS = getattr(settings,
                                   'USERENA_REMEMBER_ME_DAYS',
                                   (gettext('a month'), 30))

USERENA_FORBIDDEN_USERNAMES = getattr(settings,
                                      'USERENA_FORBIDDEN_USERNAMES',
                                      ('signup', 'signout', 'signin',
                                       'activate', 'me', 'password'))

USERENA_MUGSHOT_GRAVATAR = getattr(settings,
                                   'USERENA_MUGSHOT_GRAVATAR',
                                   True)

USERENA_MUGSHOT_DEFAULT = getattr(settings,
                                  'USERENA_MUGSHOT_DEFAULT',
                                  'identicon')

USERENA_MUGSHOT_SIZE = getattr(settings,
                               'USERENA_MUGSHOT_SIZE',
                               80)

USERENA_MUGSHOT_PATH = getattr(settings,
                               'USERENA_MUGSHOT_PATH',
                               'mugshots/')

USERENA_USE_HTTPS = getattr(settings,
                            'USERENA_USE_HTTPS',
                            False)

USERENA_DEFAULT_PRIVACY = getattr(settings,
                                  'USERENA_DEFAULT_PRIVACY',
                                  'registered')

USERENA_DISABLE_PROFILE_LIST = getattr(settings,
                                       'USERENA_DISABLE_PROFILE_LIST',
                                       False)

USERENA_USE_MESSAGES = getattr(settings,
                               'USERENA_USE_MESSAGES',
                               True)

USERENA_LANGUAGE_FIELD = getattr(settings,
                                 'USERENA_LANGUAGE_FIELD',
                                 'language')

USERENA_WITHOUT_USERNAMES = getattr(settings,
                                    'USERENA_WITHOUT_USERNAMES',
                                    False)
