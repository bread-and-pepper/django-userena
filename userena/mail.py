# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.core.mail import EmailMultiAlternatives

from userena import settings as userena_settings

from html2text import html2text

def send_mail(subject, message_plain, message_html, email_from, email_to,
              custom_headers={}, attachments=()):
    """
    Build the email as a multipart message containing
    a multipart alternative for text (plain, HTML) plus
    all the attached files.
    """
    if not message_plain and not message_html:
        raise ValueError(_("Either message_plain or message_html should be not None"))

    if not message_plain:
        message_plain = html2text(message_html)

    message = {}

    message['subject'] = subject
    message['body'] = message_plain
    message['from_email'] = email_from
    message['to'] = email_to
    if attachments:
        message['attachments'] = attachments
    if custom_headers:
        message['headers'] = custom_headers

    msg = EmailMultiAlternatives(**message)
    if message_html:
        msg.attach_alternative(message_html, "text/html")
    msg.send()


def wrap_attachment():
    pass


class UserenaConfirmationMail(object):

    _message_txt = 'userena/emails/{0}_email_message{1}.txt'
    _message_html = 'userena/emails/{0}_email_message{1}.html'
    _subject_txt = 'userena/emails/{0}_email_subject{1}.txt'

    def __init__(self, context):
        self.context = context

    def generate_mail(self, type_mail, version=""):
        self.type_mail = type_mail
        self.message_txt = self._message_txt.format(type_mail, version)
        self.message_html = self._message_html.format(type_mail, version)
        self.subject_txt = self._subject_txt.format(type_mail, version)
        self.subject = self._subject()
        self.message_html = self._message_in_html()
        self.message = self._message_in_txt()

    def send_mail(self, email):
        send_mail(self.subject, self.message,
                  self.message_html, settings.DEFAULT_FROM_EMAIL,
                  [email])

    def _message_in_html(self):
        if userena_settings.USERENA_HTML_EMAIL:
            return render_to_string(self.message_html, self.context)
        return None

    def _message_in_txt(self):
        if (not userena_settings.USERENA_HTML_EMAIL
            or not self.message_html
            or userena_settings.USERENA_USE_PLAIN_TEMPLATE):
            return render_to_string(self.message_txt, self.context)
        return None

    def _subject(self):
        subject = render_to_string(self.subject_txt, self.context)
        subject = ''.join(subject.splitlines())
        return subject
