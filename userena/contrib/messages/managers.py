from django.db import models

class MessageManager(models.Manager):

    def inbox_for(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        return self.filter(
            recipients=user,
            messagerecipient__deleted_at__isnull=True,
            #recipient_deleted_at__isnull=True,
        )

    def outbox_for(self, user):
        """
        Returns all messages that were sent by the given user and are not
        marked as deleted.

        """
        return self.filter(
            sender=user,
            sender_deleted_at__isnull=True,
            sent_at__isnull=False,
        )

    def trash_for(self, user):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.

        """
        return self.filter(
            recipients=user,
            messagerecipient__deleted_at__isnull=False,
        ) | self.filter(
            sender=user,
            sender_deleted_at__isnull=False,
        )

    def drafts_for(self, user):
        """
        Returns all messages where ``sent_at`` is Null and where the given
        user is the sender and which are not yet deleted by the sender.
        """
        return self.filter(
            sender=user,
            sent_at__isnull=True,
            sender_deleted_at__isnull=True,
        )
