from django.test import TestCase
from django.contrib.auth.models import User

from userena.contrib.umessages.models import Message

class MessageManagerTests(TestCase):
    fixtures = ['users', 'messages']

    def test_get_inbox(self):
        """ Test the manager for getting messages from the inbox """
        user = User.objects.get(pk=1)
        inbox_messages = Message.objects.get_inbox_for(user)

        self.failUnlessEqual(len(inbox_messages), 1)
        self.failUnlessEqual(inbox_messages[0].body,
                             'Hello from your mother')

    def test_get_outbox(self):
        """ Test the manager for getting messages from the outbox """
        user = User.objects.get(pk=1)
        outbox_messages = Message.objects.get_outbox_for(user)

        self.failUnlessEqual(len(outbox_messages), 1)
        self.failUnlessEqual(outbox_messages[0].body,
                             'Hello from your friend')

    def test_get_trash(self):
        """ Test the manager for getting removed messages """
        user = User.objects.get(pk=2)
        removed_messages = Message.objects.get_trash_for(user)

        self.failUnlessEqual(len(removed_messages), 1)
        self.failUnlessEqual(removed_messages[0].body,
                             "Hello from your mother")

    def test_invalid_folder(self):
        """ Test that an invalid folder raises ``ValueError`` """
        user = User.objects.get(pk=1)
        self.assertRaises(ValueError, Message.objects.get_mailbox_for,
                          user, 'fake')

    def test_get_conversation(self):
        """ Test that the conversation is returned between two users """
        user_1 = User.objects.get(pk=1)
        user_2 = User.objects.get(pk=2)

        messages = Message.objects.get_conversation_between(user_1, user_2)
