from setuptools import setup, find_packages
import sys

userena = __import__('userena')

readme_file = 'README.mkd'
try:
    long_description = open(readme_file).read()
except IOError, err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "``long_description`` (%s)\n" % readme_file)
    sys.exit(1)

setup(name='django-userena',
      version=userena.get_version(),
      description='Complete user management application for Django',
      long_description=long_description,
      zip_safe=False,
      author='Petar Radosevic',
      author_email='petar@wunki.org',
      url='https://github.com/bread-and-pepper/django-userena/',
      download_url='https://github.com/bread-and-pepper/django-userena/downloads',
      packages = find_packages(exclude=['demo_project', 'demo_project.*']),
      include_package_data=True,
      install_requires = [
        'Django>=1.3.1',
        'easy_thumbnails',
        'django-guardian>=0.1.0',
        ### Required to build documentation
        # 'sphinx',
        # 'south',
      ],
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
