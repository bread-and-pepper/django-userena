from django.test import TestCase
from django.core.urlresolvers import reverse

class MessagesViewsTests(TestCase):
    fixtures = ['users',]

    def test_mailbox(self):
        """ A ``GET`` to the message list view """
        # Viewing without logging in should redirect.
        response = self.client.get(reverse('userena_messages_inbox'))
        self.assertEqual(response.status_code, 302)

        # After signing in.
        client = self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_messages_inbox'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'messages/message_list.html')
