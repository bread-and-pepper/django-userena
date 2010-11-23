from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class CommaSeparatedUserInput(widgets.Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif isinstance(value, (list, tuple)):
            value = (', '.join([user.username for user in value]))
        return super(CommaSeparatedUserInput, self).render(name, value, attrs)

class CommaSeparatedUserField(forms.Field):
    """
    A :class:`CharField` that exists of comma separated usernames.

    :param recipient_filter:
        A list of :class:`User` which don't whose username cannot be entered in
        the :class:`CommaSeparatedUserField``

    :return:
        A list of :class:`User`.

    """
    widget = CommaSeparatedUserInput

    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        self._recipient_filter = recipient_filter
        super(CommaSeparatedUserField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(CommaSeparatedUserField, self).clean(value)
        if not value:
            return ''
        if isinstance(value, (list, tuple)):
            return value

        names = set(value.split(','))
        names_set = set([name.strip() for name in names])
        users = list(User.objects.filter(username__in=names_set))

        # Check for unknown names.
        unknown_names = names_set ^ set([user.username for user in users])

        recipient_filter = self._recipient_filter
        invalid_users = []
        if recipient_filter is not None:
            for r in users:
                if recipient_filter(r) is False:
                    users.remove(r)
                    invalid_users.append(r.username)

        if unknown_names or invalid_users:
            raise forms.ValidationError(_("The following usernames are incorrect: %(users)s") % {'users': ', '.join(list(unknown_names) + invalid_users)})

        return users
