from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from userena.contrib.umessages.forms import ComposeForm

class MessagesViewsTests(TestCase):
    fixtures = ['users', 'messages']

    def _test_login(self, named_url, **kwargs):
        """ Test that the view requires login """
        response = self.client.get(reverse(named_url, **kwargs))
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

        self.failUnless(isinstance(response.context['form'],
                                   ComposeForm))

    def test_compose_post(self):
        """ ``POST`` to the compose view """
        client = self.client.login(username='john', password='blowfish')

        valid_data = {'to': 'john',
                      'subject': 'A test message',
                      'body': 'Hi'}

        # Check for a normal redirect
        response = self.client.post(reverse('userena_umessages_compose'),
                                    data=valid_data)

        self.assertRedirects(response,
                             reverse('userena_umessages_inbox'))

        # Check for a requested redirect
        valid_data['next'] = reverse('userena_umessages_drafts')
        response = self.client.post(reverse('userena_umessages_compose'),
                                    data=valid_data)
        self.assertRedirects(response,
                             valid_data['next'])

    def test_compose_recipients(self):
        """ A ``GET`` to the compose view with recipients """
        client = self.client.login(username='john', password='blowfish')

        valid_recipients = "john+jane"
        invalid_recipients = "johny+jane"

        # Test valid recipients
        response = self.client.get(reverse('userena_umessages_compose_to',
                                           kwargs={'recipients': valid_recipients}))

        self.assertEqual(response.status_code, 200)

        # Test the users
        jane = User.objects.get(username='jane')
        john = User.objects.get(username='john')
        self.assertEqual(response.context['recipients'][0], jane)
        self.assertEqual(response.context['recipients'][1], john)

        # Test that the initial data of the form is set.
        self.assertEqual(response.context['form'].initial['to'],
                         [jane, john])

    def test_compose_reply(self):
        """ A ``GET`` to the compose view with a parent_id """
        client = self.client.login(username='john', password='blowfish')

        # Get a valid reply
        response = self.client.get(reverse('userena_umessages_reply',
                                           kwargs={'parent_id': 2}))

        self.assertEqual(response.status_code, 200)

        # Test that the initial data of the form is set.
        self.assertEqual(response.context['form'].initial['subject'],
                         u'Re: REMOVED: I found a bug...')


        # Get an invalid reply, because your not a recipient
        response = self.client.get(reverse('userena_umessages_reply',
                                           kwargs={'parent_id': 1}))

        self.assertEqual(response.status_code, 404)

    def test_message_detail(self):
        """ A ``GET`` to the detail view """
        self._test_login('userena_umessages_detail',
                          kwargs={'message_id': 1})

        # Sign in
        client = self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_umessages_detail',
                                   kwargs={'message_id': 1}))


        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'umessages/message_detail.html')
