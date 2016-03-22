.. Userena documentation master file, created by
   sphinx-quickstart on Fri Jul  2 09:28:08 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Userena Introduction
====================

This documentation covers |release| release of django-userena application.
A Django application that takes care of your account needs.

Why userena?
================

Because we have done the hard work for you. Userena supplies you with signup,
signin, account editing, privacy settings and private messaging. All you have
to do is plug it into your project and you will have created account
management with the following options:

    - User has to **activate** their account by clicking on a activation link
      in an email sent to them.

    - **Permissions** for viewing, changing and deleting accounts is
      implemented on an user and object basis with the help of django-guardian.

    - Optionally **secure** userena by using https. If you change the settings
      to use https, userena will switch to the secure protocol on it's views
      and emails.

    - All **templates** are already supplied for you. Only override those that
      don't fit with your needs.

    - Mugshots are supplied by **Gravatar** or uploaded by the user. The
      default mugshot can be set in the settings.

    - **Messaging** system between users that either get's displayed as
      conversations (iPhone like) or sorted per subject (Gmail).

Help out
========

Found a bug in userena? File an issue at Github. Have an improvement? Fork it
and add it, or if you can't code it, contact us to do it.


Deprecation warnigns
====================

2.0.0 version:

- ``userena.utils.get_user_model()`` is deprecated and will be removed in
  version 3.0.0. Use ``django.contrib.auth.get_user_model()``


Changes and releases
====================

For changes history and available releases see following pages on GitHub
repository:

* `UDATES.md <https://github.com/django-guardian/django-guardian/blob/devel/CHANGES.md>`_
* `releases <https://github.com/django-guardian/django-guardian/releases>`_


Contents
========

.. toctree::
   :maxdepth: 2
   
   installation
   settings
   signals
   commands
   faq
   api/index

Contrib: uMessages
~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 3

   contrib/umessages/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
