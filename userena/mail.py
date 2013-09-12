# -*- coding: utf-8 -*-
import re
from StringIO import StringIO

from django.utils.translation import ugettext as _
from django.core.mail import EmailMultiAlternatives

from html2text import html2text as html2text_orig


LINK_RE = re.compile(r"https?://([^ \n]+\n)+[^ \n]+", re.MULTILINE)
def html2text(html):
    """Use html2text but repair newlines cutting urls.
    Need to use this hack until
    https://github.com/aaronsw/html2text/issues/#issue/7 is not fixed"""
    txt = html2text_orig(html)
    links = list(LINK_RE.finditer(txt))
    out = StringIO()
    pos = 0
    for l in links:
        out.write(txt[pos:l.start()])
        out.write(l.group().replace('\n', ''))
        pos = l.end()
    out.write(txt[pos:])
    return out.getvalue()

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