from setuptools import setup, find_packages

readme_file = 'README.mkd'
try:
    long_description = open(readme_file).read()
except IOError, err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "``long_description`` (%s)\n" % readme_file)
    sys.exit(1)

setup(name='django-userena',
      version='0.1.0',
      description='Complete user management application for Django',
      long_description=long_description,
      zip_safe=False,
      author='Petar Radosevic',
      author_email='petar@wunki.org',
      url='http://github.com/wunki/django-userena',
      download_url='http://github.com/wunki/django-userenity/downloads',
      packages = find_packages(),
      install_requires = [
        'Django>=1.2.1',
        'python-dateutil>=1.5',
        'pil>=1.1.6',
        'easy_thumbnails',
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
