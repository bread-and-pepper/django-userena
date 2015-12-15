#encoding:utf-8
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from userena.contrib.umessages.forms import ComposeForm


class ComposeFormTests(TestCase):
    """ Test the compose form. """
    fixtures = ['users']

    def test_invalid_data(self):
        """
        Test the save method of :class:`ComposeForm`

        We don't need to make the ``to`` field sweat because we have done that
        in the ``fields`` test.

        """
        invalid_data_dicts = [
            # No body
            {'data': {'to': 'john',
                      'body': ''},
             'error': ('body', ['This field is required.'])},
        ]

        for invalid_dict in invalid_data_dicts:
            form = ComposeForm(data=invalid_dict['data'])
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

    def test_save_msg(self):
        """ Test valid data """
        valid_data = {'to': 'john, jane',
                      'body': 'Body'}

        form = ComposeForm(data=valid_data)

        self.assertTrue(form.is_valid())

        # Save the form.
        sender = get_user_model().objects.get(username='jane')
        msg = form.save(sender)

        # Check if the values are set correctly
        self.assertEqual(msg.body, valid_data['body'])
        self.assertEqual(msg.sender, sender)
        self.assertTrue(msg.sent_at)

        # Check recipients
        self.assertEqual(msg.recipients.all()[0].username, 'jane')
        self.assertEqual(msg.recipients.all()[1].username, 'john')
