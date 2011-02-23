from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.text import truncate_words

from userena.contrib.umessages.managers import (MessageManager, MessageContactManager,
                                                MessageRecipientManager)

class MessageContact(models.Model):
    """
    Contact model.

    A contact is a user to whom a user has send a message to or
    received a message from.

    """
    from_user = models.ForeignKey(User, verbose_name=_("from user"),
                                  related_name=('from_users'))

    to_user = models.ForeignKey(User, verbose_name=_("to user"),
                                related_name=('to_users'))

    latest_message = models.ForeignKey('Message',
                                       verbose_name=_("latest message"))

    objects = MessageContactManager()

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['latest_message']
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __unicode__(self):
        return (_("%(from_user)s and %(to_user)s")
                % {'from_user': self.from_user.username,
                   'to_user': self.to_user.username})

    def opposite_user(self, user):
        """
        Returns the user opposite of the user that is given

        :param user:
            A Django :class:`User`.

        :return:
            A Django :class:`User`.

        """
        if self.from_user == user:
            return self.to_user
        else: return self.from_user

class MessageRecipient(models.Model):
    """
    Intermediate model to allow per recipient marking as
    deleted, read etc. of a message.

    """
    user = models.ForeignKey(User,
                             verbose_name=_("recipient"))

    message = models.ForeignKey('Message',
                                verbose_name=_("message"))

    read_at = models.DateTimeField(_("read at"),
                                   null=True,
                                   blank=True)

    deleted_at = models.DateTimeField(_("recipient deleted at"),
                                      null=True,
                                      blank=True)

    objects = MessageRecipientManager()

    class Meta:
        verbose_name = _("recipient")
        verbose_name_plural = _("recipients")

    def __unicode__(self):
        return (_("%(message)s")
                % {'message': self.message})

    def is_read(self):
        """ Returns a boolean whether the recipient has read the message """
        return self.read_at is None

class Message(models.Model):
    """ Private message model, from user to user(s) """
    body = models.TextField(_("body"))

    sender = models.ForeignKey(User,
                               related_name='sent_messages',
                               verbose_name=_("sender"))

    recipients = models.ManyToManyField(User,
                                        through='MessageRecipient',
                                        related_name="received_messages",
                                        verbose_name=_("recipients"))

    sent_at = models.DateTimeField(_("sent at"),
                                   auto_now_add=True)

    sender_deleted_at = models.DateTimeField(_("sender deleted at"),
                                             null=True,
                                             blank=True)

    objects = MessageManager()

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("message")
        verbose_name_plural = _("messages")

    def __unicode__(self):
        """ Human representation, displaying first ten words of the body. """
        truncated_body = truncate_words(self.body, 10)
        return "%(truncated_body)s" % {'truncated_body': truncated_body}

    def save_recipients(self, to_user_list):
        """
        Save the recipients for this message

        :param to_user_list:
            A list which elements are :class:`User` to whom the message is for.

        :return:
            Boolean indicating if any users are saved.

        """
        created = False
        for user in to_user_list:
            MessageRecipient.objects.create(user=user,
                                            message=self)
            created = True
        return created

    def update_contacts(self, to_user_list):
        """
        Updates the contacts that are used for this message.

        :param to_user_list:
            List of Django :class:`User`.

        :return:
            A boolean if a user is contact is updated.

        """
        updated = False
        for user in to_user_list:
            MessageContact.objects.update_contact(self.sender,
                                                  user,
                                                  self)
            updated = True
        return updated
