import django.core.handlers.wsgi

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'demo')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'demo.settings_dotcloud'
application = django.core.handlers.wsgi.WSGIHandler()
