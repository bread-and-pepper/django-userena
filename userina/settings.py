from django.conf import settings

# How long do people have to verify their account.
ACCOUNT_VERIFICATION_DAYS = getattr(settings, 'ACCOUNT_VERIFICATION_DAYS', 2)
