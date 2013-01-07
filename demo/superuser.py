#!/usr/bin/env python
from wsgi import *
from userena.compat import User
try:
    wunki = User.objects.get(username='wunki')
except User.DoesNotExist:
    pass
else:
    wunki.is_staff = True
    wunki.is_superuser = True
    wunki.save()
