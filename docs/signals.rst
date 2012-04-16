.. _signals:

Signals
=======

Userena contains a few signals which you can use in your own application if
you want to have custom actions when a account get's changed. All signals are
located in ``userena/signals.py`` file.

signup_complete
---------------

This signal get's fired when an user signs up at your site. Note: This doesn't
mean that the user is activated. The signal provides you with the ``user``
argument which Django's :class:`User` class.

activation_complete
-------------------

A user has succesfully activated their account. The signal provides you with
the ``user`` argument which Django's :class:`User` class.

confirmation_complete
---------------------

A user has succesfully changed their email. The signal provides you
with the ``user`` argument which Django's :class:`User` class, and the
``old_email`` argument which is the user's old email address as a
string.

password_complete
-----------------

A user has succesfully changed their password. The signal provides you with
the ``user`` argument which Django's :class:`User` class.
