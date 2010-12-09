from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.text import truncate_words

from userena.contrib.umessages.managers import MessageManager

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

    replied_at = models.DateTimeField(_("replied at"),
                                      null=True,
                                      blank=True)
    class Meta:
        verbose_name = _("recipient")
        verbose_name_plural = _("recipients")

    def __unicode__(self):
        return (_("%(message)s")
                % {'message': self.message})

    def is_read(self):
        """ Returns a boolean whether the recipient has read the message """
        return self.read_at is None

    def is_replied(self):
        """ Returns whether the recipient has written a reply to this message """
        return self.replied_at is not None

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

    parent_msg = models.ForeignKey('self',
                                   related_name='next_messages',
                                   null=True,
                                   blank=True,
                                   verbose_name=_("parent message"))

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

    @models.permalink
    def get_absolute_url(self):
        return ('userena_umessages_detail', None, {'message_id': self.pk})

    def save_recipients(self, to_user_list):
        """
        Save the recipients for this message

        :param to_user_list:
            A list which elements are :class:`User` to whom the message is for.

        """
        for user in to_user_list:
            MessageRecipient.objects.create(user=user,
                                            message=self)

class MessageContact(models.Model):
    """
    A contact model.

    """
    from_user = models.ForeignKey(User, verbose_name=_("from user"),
                                  related_name=('from_users'))

    to_user = models.ForeignKey(User, verbose_name=_("to user"),
                                related_name=('to_users'))

    latest_message = models.ForeignKey(Message,
                                       verbose_name=_("latest message"))

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['latest_message']
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __unicode__(self):
        return (_("Contact from %(from_user)s to %(to_user)s")
                % {'from_user': self.from_user.get_full_name(),
                   'to_user': self.to_user.get_full_name()})


