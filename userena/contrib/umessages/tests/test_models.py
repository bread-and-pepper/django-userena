from django.contrib.auth import get_user_model
from django.test import TestCase

from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.utils import truncate_words

User = get_user_model()


class MessageContactTests(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        contact = MessageContact.objects.get(pk=1)
        correct_format = "john and jane"
        self.assertEqual(contact.__str__(),
                             correct_format)

    def test_opposite_user(self):
        """ Test if the opposite user is returned """
        contact = MessageContact.objects.get(pk=1)
        john = User.objects.get(pk=1)
        jane = User.objects.get(pk=2)

        # Test the opposites
        self.assertEqual(contact.opposite_user(john),
                             jane)

        self.assertEqual(contact.opposite_user(jane),
                             john)

class MessageModelTests(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        message = Message.objects.get(pk=1)
        truncated_body = truncate_words(message.body, 10)
        self.assertEqual(message.__str__(),
                             truncated_body)

class MessageRecipientModelTest(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a recipient """
        recipient = MessageRecipient.objects.get(pk=1)

        valid_unicode = '%s' % (recipient.message)

        self.assertEqual(recipient.__str__(),
                             valid_unicode)

    def test_new(self):
        """ Test if the message that is new is correct """
        new_message = MessageRecipient.objects.get(pk=1)
        read_message = MessageRecipient.objects.get(pk=2)

        self.assertTrue(new_message.is_read())
        self.assertFalse(read_message.is_read())
