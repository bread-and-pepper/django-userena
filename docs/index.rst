.. Userena documentation master file, created by
   sphinx-quickstart on Fri Jul  2 09:28:08 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Userena Introduction
====================

This documentation covers 1.0 release of django-userena application. A Django
application that takes care of your account needs.

Why userena?
================

Because we have done the hard work for you. Userena supplies you with signup,
signin, account editing, privacy settings and private messaging. All you have
to do is plug it into your project and you will have a created account
management with the following options:

    - User has to **activate** their account by clicking on a activation link
      in an email send to them.

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
