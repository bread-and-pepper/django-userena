from django.core.management.base import NoArgsCommand

from userena.models import Account
from optparse import make_option

class Command(NoArgsCommand):
    """
    Search for users that still haven't verified their e-mail address after
    ``USERINA_VERIFICATION_DAYS`` and delete them.

    """
    help = 'Deletes expired users.'
    def handle_noargs(self, **options):
        users = Account.objects.delete_expired_users()
        print "Deleted %(amount)s user(s)." % {'amount': len(users)}
