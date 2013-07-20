from django.db import models
from django.db.models import Q

from userena.contrib.umessages import signals

import datetime

class MessageContactManager(models.Manager):
    """ Manager for the :class:`MessageContact` model """

    def get_or_create(self, um_from_user, um_to_user, message):
        """
        Get or create a Contact

        We override Django's :func:`get_or_create` because we want contact to
        be unique in a bi-directional manner.

        """
        created = False
        try:
            contact = self.get(Q(um_from_user=um_from_user, um_to_user=um_to_user) |
                               Q(um_from_user=um_to_user, um_to_user=um_from_user))

        except self.model.DoesNotExist:
            created = True
            contact = self.create(um_from_user=um_from_user,
                                  um_to_user=um_to_user,
                                  latest_message=message)

        return (contact, created)

    def update_contact(self, um_from_user, um_to_user, message):
        """ Get or update a contacts information """
        contact, created = self.get_or_create(um_from_user,
                                              um_to_user,
                                              message)

        # If the contact already existed, update the message
        if not created:
            contact.latest_message = message
            contact.save()
        return contact

    def get_contacts_for(self, user):
        """
        Returns the contacts for this user.

        Contacts are other users that this user has received messages
        from or send messages to.

        :param user:
            The :class:`User` which to get the contacts for.

        """
        contacts = self.filter(Q(um_from_user=user) | Q(um_to_user=user))
        return contacts

class MessageManager(models.Manager):
    """ Manager for the :class:`Message` model. """

    def send_message(self, sender, um_to_user_list, body):
        """
        Send a message from a user, to a user.

        :param sender:
            The :class:`User` which sends the message.

        :param um_to_user_list:
            A list which elements are :class:`User` to whom the message is for.

        :param message:
            String containing the message.

        """
        msg = self.model(sender=sender,
                         body=body)
        msg.save()

        # Save the recipients
        msg.save_recipients(um_to_user_list)
        msg.update_contacts(um_to_user_list)
        signals.email_sent.send(sender=None,msg=msg)

        return msg

    def get_conversation_between(self, um_from_user, um_to_user):
        """ Returns a conversation between two users """
        messages = self.filter(Q(sender=um_from_user, recipients=um_to_user,
                                 sender_deleted_at__isnull=True) |
                               Q(sender=um_to_user, recipients=um_from_user,
                                 messagerecipient__deleted_at__isnull=True))
        return messages

class MessageRecipientManager(models.Manager):
    """ Manager for the :class:`MessageRecipient` model. """

    def count_unread_messages_for(self, user):
        """
        Returns the amount of unread messages for this user

        :param user:
            A Django :class:`User`

        :return:
            An integer with the amount of unread messages.

        """
        unread_total = self.filter(user=user,
                                   read_at__isnull=True,
                                   deleted_at__isnull=True).count()

        return unread_total

    def count_unread_messages_between(self, um_to_user, um_from_user):
        """
        Returns the amount of unread messages between two users

        :param um_to_user:
            A Django :class:`User` for who the messages are for.

        :param um_from_user:
            A Django :class:`User` from whom the messages originate from.

        :return:
            An integer with the amount of unread messages.

        """
        unread_total = self.filter(message__sender=um_from_user,
                                   user=um_to_user,
                                   read_at__isnull=True,
                                   deleted_at__isnull=True).count()

        return unread_total
