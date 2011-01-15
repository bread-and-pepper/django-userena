"""
python setup.py test

"""
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = 'demo_project.settings'
from demo_project import settings

settings.INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sites',
    'demo_project.profiles',
    'guardian',
    'userena',
    'userena.contrib.umessages',
)

def main():
    from django.test.utils import get_runner
    test_runner = get_runner(settings)(interactive=False)
    failures = test_runner.run_tests(['userena', 'umessages',])
    sys.exit(failures)

if __name__ == '__main__':
    main()
