# Settings for django-userena.
# http://django-userena.org

import os
import sys
import site

HOMEDIR  = os.path.dirname(os.path.realpath(__file__))
ALLDIRS = [ HOMEDIR + '/lib/python2.6/site-packages']

prev_sys_path = list(sys.path)

for directory in ALLDIRS:
    site.addsitedir(directory)

new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
       new_sys_path.append(item)
       sys.path.remove(item)
sys.path[:0] = new_sys_path

# this will also be different for each project!
sys.path.append(HOMEDIR + '/demo_project')
sys.path.append(HOMEDIR)

os.environ['PYTHON_EGG_CACHE'] = HOMEDIR + '.python-eggs'
os.environ['DJANGO_SETTINGS_MODULE'] = 'demo_project.settings_production'

import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response): 
    environ['wsgi.url_scheme'] = environ.get('HTTP_X_URL_SCHEME', 'http') 
    return _application(environ, start_response)
