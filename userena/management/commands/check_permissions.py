from django.core.management.base import NoArgsCommand, BaseCommand
from optparse import make_option

from userena.models import UserenaSignup

class Command(NoArgsCommand):
    """
    For unknown reason, users can get wrong permissions.
    This command checks that all permissions are correct.

    """
    option_list = BaseCommand.option_list + (
        make_option('--no-output',
            action='store_false',
            dest='output',
            default=True,
            help='Hide informational output.'),
        make_option('--test',
            action='store_true',
            dest='test',
            default=False,
            help="Displays that it's testing management command. Don't use it yourself."),
        )
    
    help = 'Check that user permissions are correct.'
    def handle_noargs(self, **options):
        permissions, users, warnings  = UserenaSignup.objects.check_permissions()
        output = options.pop("output")
        test = options.pop("test")
        if test:
            self.stdout.write(40 * ".")
            self.stdout.write("\nChecking permission management command. Ignore output..\n\n")
        if output:
            for p in permissions:
                self.stdout.write("Added permission: %s\n" % p)

            for u in users:
                self.stdout.write("Changed permissions for user: %s\n" % u)

            for w in warnings:
                self.stdout.write("WARNING: %s\n" %w)

        if test:
            self.stdout.write("\nFinished testing permissions command.. continuing..\n")
