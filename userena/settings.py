from django.conf import settings

gettext = lambda s: s

# How long do people have to verify their account.
USERENA_VERIFICATION_DAYS = getattr(settings,
                                    'USERENA_VERIFICATION_DAYS',
                                    7)

# Should a notifification be send when there a only
# ``USERENA_VERIFICATION_REMEMBER_DAYS`` left before account deletion.
USERENA_VERIFICATION_NOTIFY = getattr(settings,
                                      'USERENA_VERIFICATION_NOTIFY',
                                      True)
# Amount of days before ``USERENA_VERIFICATION_DAYS`` that a 'remember to
# verify' e-mail get's send out.
USERENA_VERIFICATION_NOTIFY_DAYS = getattr(settings,
                                           'USERENA_VERIFICATION_NOTIFY_DAYS',
                                           2)

# This value will be inserted into ``Account.verification_key`` if a key get's
# used succesfully.
USERENA_VERIFIED = getattr(settings,
                           'USERENA_VERIFIED',
                           'ALREADY_VERIFIED')

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
