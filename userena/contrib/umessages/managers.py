from django.db import models
from django.db.models import Q

import datetime

class MessageManager(models.Manager):
    """ Manager for the :class:`Message` model. """

    def send_message(self, sender, to_user_list, body, parent_msg=None):
        """
        Send a message from a user, to a user.

        :param sender:
            The :class:`User` which sends the message.

        :param to_user_list:
            A list which elements are :class:`User` to whom the message is for.

        :param message:
            String containing the message.

        :param parent_msg:
            The :class:`Message` that this message originated from.

        """
        msg = self.create(sender=sender,
                          body=body)

        if parent_msg:
            msg.parent_msg = parent_msg
            msg.save()

            now = datetime.datetime.now()
            parent_msg.replied_at = now
            parent_msg.save()

        # Save the recipients
        msg.save_recipients(to_user_list)

        return msg

    def get_mailbox_for(self, user, mailbox='inbox'):
        """
        Returns all messages in the mailbox that were received by the given
        user and are not marked as deleted.

        :param user:
            The :class:`User` for who the mailbox is for.

        :param mailbox:
            String containing the mailbox which is requested. This can be
            either ``inbox``, ``outbox``, ``conversation`` or ``trash``.

        :return:
            Queryset containing :class:`Messages` or ``ValueError`` if the
            invalid mailbox is supplied.

        """
        if mailbox == 'outbox':
            messages = self.filter(sender=user,
                                   sender_deleted_at__isnull=True)

        elif mailbox == 'trash':
            received = self.filter(recipients=user,
                                   messagerecipient__deleted_at__isnull=False)

            sent = self.filter(sender=user,
                               sender_deleted_at__isnull=False)

            messages = received | sent

        elif mailbox == 'inbox':
            messages = self.filter(recipients=user,
                                   messagerecipient__deleted_at__isnull=True)

        elif mailbox == 'conversation':
            # Returns a iPhone style conversational list.
            messages = None
            pass

        else:
            raise ValueError("mailbox must be either inbox, outbox or trash")

        return messages

    def get_inbox_for(self, user):
        """ Wrapper for :func:`get_mailbox_for` to get the users inbox. """
        return self.get_mailbox_for(user, 'inbox')

    def get_outbox_for(self, user):
        """ Wrapper for :func:`get_mailbox_for` to get the users outbox. """
        return self.get_mailbox_for(user, 'outbox')

    def get_trash_for(self, user):
        """ Wrapper for :func:`get_mailbox_for` to get the users trash. """
        return self.get_mailbox_for(user, 'trash')

    def get_conversation_for(self, user, receiver):
        """ Get's a conversation between a user and it's receiver. """
        messages = self.filter(Q(recipients=receiver, sender=user) | Q(recipients=user, sender=receiver))
        return messages
