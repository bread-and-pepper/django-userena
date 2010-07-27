"""
python setup.py test

"""
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = 'demo_project.settings'
from demo_project import settings

def main():
    from django.test.utils import get_runner
    test_runner = get_runner(settings)(interactive=False)

    failures = test_runner.run_tests(['userena'])
    sys.exit(failures)

if __name__ == '__main__':
    main()
