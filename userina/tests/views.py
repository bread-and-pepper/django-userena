from django.test import TestCase
from django.core.urlresolvers import reverse

class AccountViewsTests(TestCase):
    """ Test the account views """

    def test_registration_view(self):
        """ Test the registration view """
        response = self.client.get(reverse('userina_register'))
