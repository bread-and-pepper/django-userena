from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from userena.contrib.umessages.managers import MessageManager

class Message(models.Model):
    """ Private message model, from user to user(s) """
    subject = models.CharField(_("subject"),
                               max_length=256)

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
                                   null=True,
                                   blank=True)

    sender_deleted_at = models.DateTimeField(_("sender deleted at"),
                                             null=True,
                                             blank=True)

    objects = MessageManager()

    def __unicode__(self):
        return '%s' % self.subject

    @models.permalink
    def get_absolute_url(self):
        pass

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("message")
        verbose_name_plural = _("messages")

class MessageRecipient(models.Model):
    """
    Intermediate model to allow per recipient marking as
    deleted, read etc. of a message.

    """
    user = models.ForeignKey(User,
                             verbose_name=_("recipient"))

    message = models.ForeignKey(Message,
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

    def __unicode__(self):
        return "%s (%s)" % (self.message, self.user)

    def new(self):
        """ Returns a boolean whether the recipient has read the message """
        return self.read_at is None

    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        return self.replied_at is not None

    class Meta:
        verbose_name = _("Recipient")
        verbose_name_plural = _("Recipients")
