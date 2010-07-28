from django.conf import settings

gettext = lambda s: s

# Signin redirect URL to Userena
USERENA_SIGNIN_REDIRECT_URL = getattr(settings,
                                      'USERENA_SIGNIN_REDIRECT_URL',
                                      '/accounts/%(username)s')

# How long do people have to verify their account.
USERENA_ACTIVATION_DAYS = getattr(settings,
                                  'USERENA_ACTIVATION_DAYS',
                                  7)

# Should a notifification be send when there a only
# ``USERENA_ACTIVATION_REMEMBER_DAYS`` left before account deletion.
USERENA_ACTIVATION_NOTIFY = getattr(settings,
                                    'USERENA_ACTIVATION_NOTIFY',
                                    True)

# Amount of days before ``USERENA_ACTIVATION_DAYS`` that a 'remember to
# verify' e-mail get's send out.
USERENA_ACTIVATION_NOTIFY_DAYS = getattr(settings,
                                         'USERENA_ACTIVATION_NOTIFY_DAYS',
                                         2)

# This value will be inserted into ``Account.verification_key`` if a key get's
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
                                      ('signup', 'signout', 'signin', 'verify', 'me', 'password'))

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

# Child model. Use it if more fields are needed.
USERENA_CHILD_MODEL= getattr(settings,
                             'USERENA_CHILD_MODEL',
                             None)
