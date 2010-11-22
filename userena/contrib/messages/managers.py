from django.db import models

class MessageManager(models.Manager):

    def get_mailbox_for(self, user, mailbox):
        """
        Returns all messages in the mailbox that were received by the given
        user and are not marked as deleted.

        """
        return self.filter(
            recipients=user,
            messagerecipient__deleted_at__isnull=True,
        )
