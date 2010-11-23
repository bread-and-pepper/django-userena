.. Userena documentation master file, created by
   sphinx-quickstart on Fri Jul  2 09:28:08 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Userena Introduction
====================

This documentation covers the first release of django-userena application. A
Django application that takes care of your account needs.

Want to experience it's about? Go to django-userena.org and create an account
for yourself.

Why userena?
================

Because we have done the hard work for you. Userena supplies you with signup,
signin, account editing, privacy settings for your users, etc.. Everything is
tested with unit-tests, with a 100% code coverage as goal. All you have to do
is plug it into your project and you will have all enabled the following:

    - User has to **activate** their account by clicking on a activation link
      in an email send to them.

    - **Permissions** for viewing, changing and deleting accounts is
      implemented on an user and object basis with the help of django-guardian.

    - Optionally **secure** userena by using https. If you change the settings
      to use https, userena will switch to the secure protocol on it's views
      and emails.

    - All **templates** are already supplied for you. Only override those that
      don't fit with your needs!

    - Mugshots are supplied by **Gravatar** or uploaded by the user. The
      default mugshot can be set in the settings.

    - *TODO*: Optional **Messaging** system between users and a notification
      system for administrators.

    - *TODO*: Optional **Friends** system which let's users become friends.
      Special permissions can be granted to users that are friends.

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
   commands
   api/index

Battery: Messages
~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 3

   contrib/messages/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
