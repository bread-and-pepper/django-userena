.. Userena documentation master file, created by
   sphinx-quickstart on Fri Jul  2 09:28:08 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Userena Introduction
====================

This documentation covers the first release of django-userena application. A
Django application that takes care off all your account needs. These were
selected by looking at web applications and picking those that every modern web
application needs. A few examples of these are the following: 

* After signup a user get's a activation email. A user can make use of the
  application ``USERENA_ACTIVATION_DAYS`` days before having to activate their
  account.  The user also get's a notification if their account is still not
  activated ``USERENA_ACTIVATION_NOTIFY_DAYS`` days before the activation
  key get's invalid.

* A user can signin with their e-mail address or username (as seen at Github).
  Django-userena will define which one is used and try to sign the user in with
  supplied credentials.

* At signin the user can choose to be remembered for
  ``USERENA_REMEMBER_ME_DAYS`` of time.

* Usernames defined in ``USERENA_FORBIDDEN_USERNAMES`` list are not allowed at
  signup.

* Changing your e-mail address also needs verification. Only after the URI
  inside the verification e-mail is clicked will the new e-mail address become
  active.

* Each account has their own detail page, for ex. ``/accounts/jane/`` and each
  account also has it's own settings page accessible by the owner. For ex.
  ``/accounts/me/``.

Contents
========

.. toctree::
   :maxdepth: 2
   
   installation
   settings
   commands
   forms
   views
   templates
   faq
   todo

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
