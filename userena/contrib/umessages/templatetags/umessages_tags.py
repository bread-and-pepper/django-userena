from django import template

from userena.contrib.umessages.models import MessageRecipient

import re

register = template.Library()

class MessageCount(template.Node):
    def __init__(self, um_from_user, var_name, um_to_user=None):
        self.user = template.Variable(um_from_user)
        self.var_name = var_name
        if um_to_user:
            self.um_to_user = template.Variable(um_to_user)
        else: self.um_to_user = um_to_user

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        if not self.um_to_user:
            message_count = MessageRecipient.objects.count_unread_messages_for(user)

        else:
            try:
                um_to_user = self.um_to_user.resolve(context)
            except template.VariableDoesNotExist:
                return ''

            message_count = MessageRecipient.objects.count_unread_messages_between(user,
                                                                                   um_to_user)

        context[self.var_name] = message_count

        return ''

@register.tag
def get_unread_message_count_for(parser, token):
    """
    Returns the unread message count for a user.

    Syntax::

        {% get_unread_message_count_for [user] as [var_name] %}

    Example usage::

        {% get_unread_message_count_for pero as message_count %}

    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%s tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    user, var_name = m.groups()
    return MessageCount(user, var_name)

@register.tag
def get_unread_message_count_between(parser, token):
    """
    Returns the unread message count between two users.

    Syntax::

        {% get_unread_message_count_between [user] and [user] as [var_name] %}

    Example usage::

        {% get_unread_message_count_between funky and wunki as message_count %}

    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%s tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) and (.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%s tag had invalid arguments" % tag_name)
    um_from_user, um_to_user, var_name = m.groups()
    return MessageCount(um_from_user, var_name, um_to_user)
