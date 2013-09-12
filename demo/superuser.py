#!/usr/bin/env python
from wsgi import *
from userena.utils import get_user_model
try:
    wunki = get_user_model().objects.get(username='wunki')
except get_user_model().DoesNotExist:
    pass
else:
    wunki.is_staff = True
    wunki.is_superuser = True
    wunki.save()
