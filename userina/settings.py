from django.conf import settings

gettext = lambda s: s

# How long do people have to verify their account.
USERINA_VERIFICATION_DAYS = getattr(settings, 'USERINA_VERIFICATION_DAYS', 7)

# Should a notifification be send when there a only
# ``USERINA_VERIFICATION_REMEMBER_DAYS`` left before account deletion.
USERINA_VERIFICATION_NOTIFY = getattr(settings,
                                      'USERINA_VERIFICATION_NOTIFY',
                                      True)
# Amount of days before ``USERINA_VERIFICATION_DAYS`` that a 'remember to
# verify' e-mail get's send out.
USERINA_VERIFICATION_NOTIFY_DAYS = getattr(settings,
                                           'USERINA_VERIFICATION_NOTIFY_DAYS',
                                           2)

# This value will be inserted into ``Account.verification_key`` if a key get's
# used succesfully.
USERINA_VERIFIED = getattr(settings, 'USERINA_VERIFIED', 'ALREADY_VERIFIED')

# The amount of weeks a user can choose te be remembered.
USERINA_REMEMBER_ME_DAYS = getattr(settings,
                                   'USERINA_REMEMBER_ME_DAYS',
                                   (gettext('a month'), 30))

# Forbidden usernames.
USERINA_FORBIDDEN_USERNAMES = ('signup', 'signout', 'signin', 'verify', 'me', 'password')
