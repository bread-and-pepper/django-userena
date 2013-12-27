from django.test import TestCase

from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.utils import get_user_model, truncate_words

User = get_user_model()

class MessageContactTests(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        contact = MessageContact.objects.get(pk=1)
        correct_format = "john and jane"
        self.failUnlessEqual(contact.__unicode__(),
                             correct_format)

    def test_opposite_user(self):
        """ Test if the opposite user is returned """
        contact = MessageContact.objects.get(pk=1)
        john = User.objects.get(pk=1)
        jane = User.objects.get(pk=2)

        # Test the opposites
        self.failUnlessEqual(contact.opposite_user(john),
                             jane)

        self.failUnlessEqual(contact.opposite_user(jane),
                             john)

class MessageModelTests(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        message = Message.objects.get(pk=1)
        truncated_body = truncate_words(message.body, 10)
        self.failUnlessEqual(message.__unicode__(),
                             truncated_body)

class MessageRecipientModelTest(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a recipient """
        recipient = MessageRecipient.objects.get(pk=1)

        valid_unicode = '%s' % (recipient.message)

        self.failUnlessEqual(recipient.__unicode__(),
                             valid_unicode)

    def test_new(self):
        """ Test if the message that is new is correct """
        new_message = MessageRecipient.objects.get(pk=1)
        read_message = MessageRecipient.objects.get(pk=2)

        self.failUnless(new_message.is_read())
        self.failIf(read_message.is_read())
