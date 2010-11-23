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
        self.failUnlessEqual(inbox_messages[0].subject,
                             'REMOVED: I found a bug...')

    def test_get_outbox(self):
        """ Test the manager for getting messages from the outbox """
        user = User.objects.get(pk=1)
        outbox_messages = Message.objects.get_outbox_for(user)

        self.failUnlessEqual(len(outbox_messages), 1)
        self.failUnlessEqual(outbox_messages[0].subject,
                             'UNREAD: Do you want a pizza?')

    def test_get_drafts(self):
        """ Test the manager for getting drafted messages """
        user = User.objects.get(pk=1)
        draft_messages = Message.objects.get_drafts_for(user)

        self.failUnlessEqual(len(draft_messages), 1)
        self.failUnlessEqual(draft_messages[0].subject,
                             'DRAFT: You hungry?')

    def test_get_trash(self):
        """ Test the manager for getting removed messages """
        user = User.objects.get(pk=2)
        removed_messages = Message.objects.get_trash_for(user)

        self.failUnlessEqual(len(removed_messages), 1)
        self.failUnlessEqual(removed_messages[0].subject,
                             'REMOVED: I found a bug...')
