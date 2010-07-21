from django.core.management.base import NoArgsCommand

from userena.models import Account
from optparse import make_option

class Command(NoArgsCommand):
    """
    Search for users which account is almost expired and send them a
    notification.

    """
    help = 'Sends a notification to users that are almost expired.'
    def handle_noargs(self, **options):
        users = Account.objects.notify_almost_expired()
        print "Notified %(amount)s user(s)." % {'amount': len(users)}
