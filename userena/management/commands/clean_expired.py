from django.core.management.base import BaseCommand

from userena.models import UserenaSignup

class Command(BaseCommand):
    """
    Search for users that still haven't verified their email after
    ``USERENA_ACTIVATION_DAYS`` and delete them.

    """
    help = 'Deletes expired users.'
    def handle(self, *args, **kwargs):
        users = UserenaSignup.objects.delete_expired_users()
