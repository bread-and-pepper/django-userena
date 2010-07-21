from django.test import TestCase
from userina.utils import get_gravatar

import hashlib

class UtilsTests(TestCase):
    """ Test the extra utils methods """

    def test_get_gravatar(self):
        template = 'http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(type)s'

        # The hash for alice@example.com
        hash = hashlib.md5('alice@example.com').hexdigest()

        # Check the defaults.
        self.failUnlessEqual(get_gravatar('alice@example.com'),
                             template % {'hash': hash,
                                         'size': 80,
                                         'type': 'identicon'})

        # Check different size
        self.failUnlessEqual(get_gravatar('alice@example.com', size=200),
                             template % {'hash': hash,
                                         'size': 200,
                                         'type': 'identicon'})

        # Check different default
        http_404 = get_gravatar('alice@example.com', default=404)
        self.failUnlessEqual(http_404,
                             template % {'hash': hash,
                                         'size': 80,
                                         'type': 404})

        # Is it really a 404?
        response = self.client.get(http_404)
        self.failUnlessEqual(response.status_code, 404)
