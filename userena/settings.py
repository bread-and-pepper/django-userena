# Userena settings file.
#
# Please consult the docs for more information about each setting.

from django.conf import settings
gettext = lambda s: s


USERENA_SIGNIN_AFTER_SIGNUP = getattr(settings,
                                      'USERENA_SIGNIN_AFTER_SIGNUP',
                                      False)

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

USERENA_ACTIVATION_RETRY = getattr(settings,
                                    'USERENA_ACTIVATION_RETRY',
                                    False)

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
DEFAULT_USERENA_USE_HTTPS = False

# NOTE: It is only for internal use. All those settings should be refactored to only defaults
#       as specified in #452
_USERENA_USE_HTTPS = getattr(settings, 'USERENA_USE_HTTPS', DEFAULT_USERENA_USE_HTTPS)


USERENA_MUGSHOT_GRAVATAR = getattr(settings,
                                   'USERENA_MUGSHOT_GRAVATAR',
                                   True)

USERENA_MUGSHOT_GRAVATAR_SECURE = getattr(settings,
                                          'USERENA_MUGSHOT_GRAVATAR_SECURE',
                                          _USERENA_USE_HTTPS)

USERENA_MUGSHOT_DEFAULT = getattr(settings,
                                  'USERENA_MUGSHOT_DEFAULT',
                                  'identicon')

USERENA_MUGSHOT_SIZE = getattr(settings,
                               'USERENA_MUGSHOT_SIZE',
                               80)

USERENA_MUGSHOT_CROP_TYPE = getattr(settings,
                                    'USERENA_MUGSHOT_CROP_TYPE',
                                    'smart')

USERENA_MUGSHOT_PATH = getattr(settings,
                               'USERENA_MUGSHOT_PATH',
                               'mugshots/')

USERENA_DEFAULT_PRIVACY = getattr(settings,
                                  'USERENA_DEFAULT_PRIVACY',
                                  'registered')

USERENA_DISABLE_PROFILE_LIST = getattr(settings,
                                       'USERENA_DISABLE_PROFILE_LIST',
                                       False)

USERENA_DISABLE_SIGNUP = getattr(settings,
                                 'USERENA_DISABLE_SIGNUP',
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

USERENA_PROFILE_DETAIL_TEMPLATE = getattr(
    settings, 'USERENA_PROFILE_DETAIL_TEMPLATE', 'userena/profile_detail.html')

USERENA_PROFILE_LIST_TEMPLATE = getattr(
    settings, 'USERENA_PROFILE_LIST_TEMPLATE', 'userena/profile_list.html')

USERENA_HIDE_EMAIL = getattr(settings, 'USERENA_HIDE_EMAIL', False)

USERENA_HTML_EMAIL = getattr(settings, 'USERENA_HTML_EMAIL', False)

USERENA_USE_PLAIN_TEMPLATE = getattr(settings, 'USERENA_USE_PLAIN_TEMPLATE', not USERENA_HTML_EMAIL)

USERENA_REGISTER_PROFILE = getattr(settings, 'USERENA_REGISTER_PROFILE', True)

USERENA_REGISTER_USER = getattr(settings, 'USERENA_REGISTER_USER', True)
