from django.test import TestCase
from django import forms

from userena.contrib.umessages.fields import CommaSeparatedUserField

class CommaSeparatedTestForm(forms.Form):
    users = CommaSeparatedUserField()

    def __init__(self, *args, **kwargs):
        super(CommaSeparatedTestForm, self).__init__(*args, **kwargs)
        self.fields['users']._recipient_filter = self.filter_jane

    def filter_jane(self, user):
        if user.username == 'jane':
            return False
        return True

class CommaSeperatedFieldTests(TestCase):
    fixtures = ['users',]

    def test_invalid_data(self):
        # Test invalid data supplied to the field.
        invalid_data_dicts = [
            # Empty username
            {'data': {'users': ''},
             'error': ('users', [u'This field is required.'])},
            # No data
            {'data': {},
             'error': ('users', [u'This field is required.'])},
            # A list
            {'data': {'users': []},
             'error': ('users', [u'This field is required.'])},
            # Forbidden username
            {'data': {'users': 'jane'},
             'error': ('users', [u'The following usernames are incorrect: jane.'])},
            # Non-existant username
            {'data': {'users': 'foo'},
             'error': ('users', [u'The following usernames are incorrect: foo.'])},
            # Multiple invalid usernames
            {'data': {'users': 'foo, bar'},
             'error': ('users', [u'The following usernames are incorrect: foo, bar.'])},
            # Valid and invalid
            {'data': {'users': 'foo, john, bar'},
             'error': ('users', [u'The following usernames are incorrect: foo, bar.'])},
            # Extra whitespace
            {'data': {'users': 'foo,    john  '},
             'error': ('users', [u'The following usernames are incorrect: foo.'])},

        ]
        for invalid_dict in invalid_data_dicts:
            form = CommaSeparatedTestForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])
