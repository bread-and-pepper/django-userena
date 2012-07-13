#!/usr/bin/env python
from wsgi import *
from django.contrib.auth.models import User
try:
    wunki = User.objects.get(username='wunki')
except User.DoesNotExist:
    pass
else:
    wunki.is_staff = True
    wunki.is_superuser = True
    wunki.save()
