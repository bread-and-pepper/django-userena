#!/usr/bin/env python
from django.core.management import execute_manager
try:
    import socket
    if socket.gethostname() == 'breadandpepper.com':
        import settings_production as settings
    else:
        import settings
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
