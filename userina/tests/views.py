from django.test import TestCase
from django.core.urlresolvers import reverse

class AccountViewsTests(TestCase):
    """ Test the account views """

    def test_signup_view(self):
        """ Test the signup view """
        response = self.client.get(reverse('userina_signup'))
