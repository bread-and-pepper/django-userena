from django import forms
from django.utils.translation import ugettext_lazy as _

from userena.contrib.umessages.fields import CommaSeparatedUserField
from userena.contrib.umessages.models import Message, MessageRecipient

import datetime

class ComposeForm(forms.Form):
    to = CommaSeparatedUserField(label=_("To"))
    subject = forms.CharField(max_length=256,
                              label=_("Subject"))

    body = forms.CharField(label=_("Message"),
                           widget=forms.Textarea({'class': 'message'}),
                           required=True)

    def save(self, sender, parent_msg, draft=False):
        """
        Save the message and send it out into the wide world.

        :param sender:
            The :class:`User` that sends the message.

        :param parent_msg:
            The :class:`Message` that preceded this message in the thread.

        :param draft:
            ``Boolean`` defining this message as draft. Defaults to ``False``.

        :return: The saved :class:`Message`.

        """
        to_list = self.cleaned_data['to']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']

        now = datetime.datetime.now()

        # Save the message
        msg = Message(sender=sender, subject=subject, body=body)
        if not draft:
            msg.sent_at = now
            if parent_msg:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = now
                parent_msg.save()
        msg.save()

        # Save the recipients
        for r in to_list:
            mr = MessageRecipient(message=msg,
                                  user=r)
            mr.save()

        return msg
