from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.text import truncate_words

from userena.contrib.umessages.models import Message, MessageRecipient

class MessageModelTests(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        message = Message.objects.get(pk=1)
        truncated_body = truncate_words(message.body, 10)
        self.failUnlessEqual(message.__unicode__(),
                             truncated_body)

    def test_absolute_url(self):
        """ Test the absolute url of a message """
        message = Message.objects.get(pk=1)
        self.failUnlessEqual(message.get_absolute_url(),
                             reverse('userena_umessages_detail',
                                     kwargs={'message_id': 1}))

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

    def test_replied(self):
        """ Test that replied messages are correctly shown """
        not_replied_message = MessageRecipient.objects.get(pk=1)
        replied_message = MessageRecipient.objects.get(pk=2)

        self.failIf(not_replied_message.is_replied())
        self.failUnless(replied_message.is_replied())
