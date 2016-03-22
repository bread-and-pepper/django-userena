# UPDATES

This file contains all the backwards-incompatible (since 1.0.1) and other
significant (since 1.4.1) changes.


## Version 2.0.0

Backwards incompatible changes:

- Drop support for Django 1.4
- Add support for Django 1.9
- Added new Django 1.9 migration for `userena` and `userena.contrib.umessages`.
  Old South migrations are still available in `userena.south_migrations` and
  `userena.contrib.umessages.south_migrations` but are deprecated and may be
  removed in future major releases. `South>1.0` is required for older versions
  of Django.
- `django-guardian` requirement bumped to `<=1.4.1` as newer version (1.4.2)
  fails on tests.
- removed all `{% load url from future %}` from userena templates for
  compatibility with Django 1.9
- `sha_constructor()`, `smart_text()`, and `md5_constructor` removed from
  `userena.compat`
- Use simple list literal as url patterns instead of
  `django.conf.urls.patterns()` function

Deprecated features:

- `userena.utils.get_user_model` is deprecated and will be removed in version
   3.0.0. Use `django.contrib.auth.get_user_model`

Fixes and improvements:

- More nodes added to the travis test matrix.
- Some documentation moved to `.md` files.
- Deprecated unittest aliases replaced in tests.
- Updated list of trove classifiers.
- Added option to execute `runtests` script with pattern parameter to limit
  number of tests.
- Added `{posargs}` to test command execution in `tox.ini` to improve developer
  experience during tests.
- Minor documentation improvements.
- Set `django-guardian<1.4.0` version for Django 1.5 and 1.6 tests.


## Version 1.5.1

- Update url patterns to handle usernames starting with 'signup', 'signin',
  'signout' strings (#502)

## Version 1.5.0

Fixes and improvements:

- Updated Norwegian translations and fixed issue with unicode characters sent
  to `utils.generate_sha1` (#472)
- Fix `upload_to_mugshot` if model uses primary key diffrent than `id` (#475)
- Minor compatibility improvements (#485)
- Refactored mailer (#486)
- Password reset email now inlcudes email template for django>=1.7 (#493)
- Fixes to translations (#499)
- Added Romanian translations (#500)

Backwards incompatible changes:

- django-guardian has version fixed to `<=1.3.1` due to django 1.4 compatibility


## Version 1.4.1

Fixes and improvements:

- Set `html2text==2014.12.29` requirement in order to remove nasty hack
  in `userena/mail.py` (#462).
- Updated version in Sphinx docs (#461).
- Added support for Python3.2 (#453).
- Fixed issue causing malformed utf-8 usernames on user profile creation (#456).
- Fixed issue with user creation on Python3.4 (#455).
- Fixed randomly failing tests on travis (#446).


## Version 1.4.0

Fixes and improvements:

- Python3.3 and Python3.4 support added.


## Version 1.3.2

Backwards incompatible changes:

- Creating new user always creates new empty userena profile (fixes bug from 1.3.1).


## Version 1.3.1

Backwards incompatible changes:

- When USERENA_ACTIVATION_REQUIRED = False, creating new user does not automatically
  create userena profile (bug).


## Version 1.2.2

Backwards incompatible changes:

- Changed backwards relationships names for Umessages contrib application from
  `to_user` to `um_to_user` and `from_user` to `um_from_user`.


## Version 1.2.0

Backwards incompatible changes:

- This version updates Userena to be able to use the new `User` model found in
  Django 1.5. This does require the django-guardion > 1.5-dev. To make this
  work, there is a `get_user_model` function in `userena/utils.py` which is used
  to get the correct `User` model.


## Version 1.1.2

Backwards incompatible changes:

- Activation view no longer contains username. If you override
  `userena/templates/userena/emails/activation_email_message.txt` and
  `userena/templates/userena/emails/confirmation_email_message_new.txt` be sure
  to remove username from the URL.


## Version 1.1

Backwards incompatible changes:

- Userena now requires Django >= 1.3 because of the use of class based views.


## Version 1.0.1

Backwards incompatible changes:

- Removed the ``user`` relationship outside ``UserenaBaseProfile`` model. This
  allows the user to define it's own relationship and fixes a conflict while
  running ``manage.py test``. To migrate, place the ``user`` field inside your
  profile model, instead of inheriting it from the ``abstract`` class.
