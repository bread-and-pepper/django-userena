from setuptools import setup, find_packages
import sys

userena = __import__('userena')

readme_file = 'README.mkd'
try:
    long_description = open(readme_file).read()
except IOError:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "``long_description`` (%s)\n" % readme_file)
    sys.exit(1)

install_requires = ['easy_thumbnails', 'django-guardian', 'html2text']
try:
    from collections import OrderedDict
except ImportError:
    install_requires.append('ordereddict')

setup(name='django-userena',
      version=userena.get_version(),
      description='Complete user management application for Django',
      long_description=long_description,
      zip_safe=False,
      author='Petar Radosevic',
      author_email='petar@wunki.org',
      url='https://github.com/bread-and-pepper/django-userena/',
      download_url='https://github.com/bread-and-pepper/django-userena/downloads',
      packages = find_packages(exclude=['demo', 'demo.*']),
      include_package_data=True,
      install_requires = install_requires,
      test_suite='tests.main',
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Web Environment',
                     'Framework :: Django',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Utilities'],
      )
