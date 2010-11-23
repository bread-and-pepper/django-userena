from django.test import TestCase
from django.core.urlresolvers import reverse

class MessagesViewsTests(TestCase):
    fixtures = ['users',]

    def _test_login(self, named_url):
        """ Test that the view requires login """
        response = self.client.get(reverse(named_url))
        self.assertEqual(response.status_code, 302)

    def test_mailbox(self):
        """ A ``GET`` to the message list view """
        # Viewing without logging in should redirect.
        self._test_login('userena_umessages_inbox')

        # After signing in.
        client = self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_umessages_inbox'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'umessages/message_list.html')

    def test_compose(self):
        """ A ``GET`` to the compose view """
        # Login is required.
        self._test_login('userena_umessages_compose')

        # Sign in
        client = self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_umessages_compose'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'umessages/compose_form.html')
