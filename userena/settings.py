from django.conf import settings

gettext = lambda s: s

# Signin redirect URL to Userena
USERENA_SIGNIN_REDIRECT_URL = getattr(settings,
                                      'USERENA_SIGNIN_REDIRECT_URL',
                                      '/accounts/%(username)s/')

# How long do people have to activate.
USERENA_ACTIVATION_DAYS = getattr(settings,
                                  'USERENA_ACTIVATION_DAYS',
                                  7)

# Should a notifification be send when there a only
# ``USERENA_ACTIVATION_REMEMBER_DAYS`` left before deletion.
USERENA_ACTIVATION_NOTIFY = getattr(settings,
                                    'USERENA_ACTIVATION_NOTIFY',
                                    True)

# Amount of ``USERENA_ACTIVATION_DAYS`` days after signup that a 'remember to
# activate' e-mail get's send out if the user is still not activated.
USERENA_ACTIVATION_NOTIFY_DAYS = getattr(settings,
                                         'USERENA_ACTIVATION_NOTIFY_DAYS',
                                         5)

# This value will be inserted into ``UserenaUser.activation_key`` if a key get's
# used succesfully.
USERENA_ACTIVATED = getattr(settings,
                            'USERENA_ACTIVATED',
                            'ALREADY_ACTIVATED')

# The amount of weeks a user can choose te be remembered.
USERENA_REMEMBER_ME_DAYS = getattr(settings,
                                   'USERENA_REMEMBER_ME_DAYS',
                                   (gettext('a month'), 30))

# Forbidden usernames.
USERENA_FORBIDDEN_USERNAMES = getattr(settings,
                                      'USERENA_FORBIDDEN_USERNAMES',
                                      ('signup', 'signout', 'signin',
                                       'activate', 'me', 'password'))

# Should Gravatar be used as a backup for mugshots?
USERENA_MUGSHOT_GRAVATAR = getattr(settings,
                                   'USERENA_USE_GRAVATAR',
                                   True)

# Default image used for gravatar
USERENA_MUGSHOT_DEFAULT = getattr(settings,
                                   'USERENA_MUGSHOT_DEFAULT',
                                   'identicon')

# Size of the mugshot image (square)
USERENA_MUGSHOT_SIZE = getattr(settings,
                               'USERENA_MUGSHOT_SIZE',
                               80)

# The directory where the mugshots will be saved
USERENA_MUGSHOT_PATH = getattr(settings,
                               'USERENA_MUGSHOT_PATH',
                               'mugshots/')

# Should some of the views forced to use HTTPS.
USERENA_USE_HTTPS = getattr(settings,
                            'USERENA_USE_HTTPS',
                            False)

USERENA_DEFAULT_PRIVACY = getattr(settings,
                                  'USERENA_DEFAULT_PRIVACY',
                                  'registered')

# Disable the listing of profiles
USERENA_DISABLE_PROFILE_LIST = getattr(settings,
                                       'USERENA_DISABLE_PROFILE_LIST',
                                       False)

USERENA_USE_MESSAGES = getattr(settings,
                               'USERENA_USE_MESSAGES',
                               True)
