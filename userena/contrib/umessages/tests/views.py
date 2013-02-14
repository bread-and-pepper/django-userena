from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from userena.contrib.umessages.forms import ComposeForm
from userena.contrib.umessages.models import Message, MessageRecipient
from userena.utils import get_user_model

User = get_user_model()


class MessagesViewsTests(TestCase):
    fixtures = ['users', 'messages']

    def _test_login(self, named_url, **kwargs):
        """ Test that the view requires login """
        response = self.client.get(reverse(named_url, **kwargs))
        self.assertEqual(response.status_code, 302)

    def test_compose(self):
        """ A ``GET`` to the compose view """
        # Login is required.
        self._test_login('userena_umessages_compose')

        # Sign in
        client = self.client.login(username='john', password='blowfish')
        response = self.client.get(reverse('userena_umessages_compose'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'umessages/message_form.html')

        self.failUnless(isinstance(response.context['form'],
                                   ComposeForm))

    def test_compose_post(self):
        """ ``POST`` to the compose view """
        client = self.client.login(username='john', password='blowfish')

        valid_data = {'to': 'john',
                      'body': 'Hi'}

        # Check for a normal redirect
        response = self.client.post(reverse('userena_umessages_compose'),
                                    data=valid_data)

        self.assertRedirects(response,
                             reverse('userena_umessages_detail',
                                     kwargs={'username': 'john'}))

        # Check for a requested redirect
        valid_data['next'] = reverse('userena_umessages_compose')
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

    def test_message_detail(self):
        """ A ``GET`` to the detail view """
        self._test_login('userena_umessages_detail',
                          kwargs={'message_id': 2})

        # Sign in
        client = self.client.login(username='jane', password='blowfish')
        response = self.client.get(reverse('userena_umessages_detail',
                                   kwargs={'message_id': 1}))


        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'umessages/message_detail.html')

        # Test that the message is read.
        jane = User.objects.get(pk=2)
        mr = MessageRecipient.objects.get(message=Message.objects.get(pk=1),
                                          user=jane)
        self.failUnless(mr.read_at)

    def test_valid_message_remove(self):
        """ ``POST`` to remove a message """
        # Test that sign in is required
        response = self.client.post(reverse('userena_umessages_remove'))
        self.assertEqual(response.status_code, 302)

        # Sign in
        client = self.client.login(username='john', password='blowfish')

        # Test that only posts are allowed
        response = self.client.get(reverse('userena_umessages_remove'))
        self.assertEqual(response.status_code, 405)

        # Test a valid post to delete a senders message
        response = self.client.post(reverse('userena_umessages_remove'),
                                    data={'message_pks': '1'})
        self.assertRedirects(response,
                             reverse('userena_umessages_list'))
        msg = Message.objects.get(pk=1)
        self.failUnless(msg.sender_deleted_at)

        # Test a valid post to delete a recipients message and a redirect
        client = self.client.login(username='jane', password='blowfish')
        response = self.client.post(reverse('userena_umessages_remove'),
                                    data={'message_pks': '1',
                                          'next': reverse('userena_umessages_list')})
        self.assertRedirects(response,
                             reverse('userena_umessages_list'))
        jane = User.objects.get(username='jane')
        mr = msg.messagerecipient_set.get(user=jane,
                                          message=msg)
        self.failUnless(mr.deleted_at)

    def test_invalid_message_remove(self):
        """ ``POST`` to remove an invalid message """
        # Sign in
        client = self.client.login(username='john', password='blowfish')

        bef_len = Message.objects.filter(sender_deleted_at__isnull=False).count()
        response = self.client.post(reverse('userena_umessages_remove'),
                                    data={'message_pks': ['a', 'b']})

        # The program should play nice, nothing happened.
        af_len = Message.objects.filter(sender_deleted_at__isnull=False).count()
        self.assertRedirects(response,
                             reverse('userena_umessages_list'))
        self.assertEqual(bef_len, af_len)

    def test_valid_message_remove_multiple(self):
        """ ``POST`` to remove multiple messages """
        # Sign in
        client = self.client.login(username='john', password='blowfish')
        response = self.client.post(reverse('userena_umessages_remove'),
                                    data={'message_pks': [1, 2]})
        self.assertRedirects(response,
                             reverse('userena_umessages_list'))

        # Message #1 and #2 should be deleted
        msg_list = Message.objects.filter(pk__in=['1','2'],
                                          sender_deleted_at__isnull=False)
        self.assertEqual(msg_list.count(), 2)

    def test_message_unremove(self):
        """ Unremove a message """
        client = self.client.login(username='john', password='blowfish')

        # Delete a message as owner
        response = self.client.post(reverse('userena_umessages_unremove'),
                                    data={'message_pks': [1,]})

        self.assertRedirects(response,
                             reverse('userena_umessages_list'))

        # Delete the message as a recipient
        response = self.client.post(reverse('userena_umessages_unremove'),
                                    data={'message_pks': [2,]})

        self.assertRedirects(response,
                             reverse('userena_umessages_list'))

    def test_message_list(self):
        """ ``GET`` the message list for a user """
        self._test_login("userena_umessages_list")

        client = self.client.login(username="john", password="blowfish")
        response = self.client.get(reverse("userena_umessages_list"))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "umessages/message_list.html")

    def test_message_detail(self):
        """ ``GET`` to a detail page between two users """
        self._test_login("userena_umessages_detail",
                         kwargs={'username': "jane"})
        client = self.client.login(username='john', password='blowfish')

        response = self.client.get(reverse("userena_umessages_detail",
                                           kwargs={'username': "jane"}))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "umessages/message_detail.html")

        # Check that all the messages are marked as read.
        john = User.objects.get(pk=1)
        jane = User.objects.get(pk=2)
        unread_messages = MessageRecipient.objects.filter(user=john,
                                                          message__sender=jane,
                                                          read_at__isnull=True)

        self.assertEqual(len(unread_messages), 0)
