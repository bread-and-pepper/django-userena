from django.core.management.base import NoArgsCommand

from userena.models import UserenaSignup

class Command(NoArgsCommand):
    """
    For unknown reason, users can get wrong permissions.
    This command checks that all permissions are correct.

    """
    help = 'Check that user permissions are correct.'
    def handle_noargs(self, **options):
        users = UserenaSignup.objects.check_permissions()
