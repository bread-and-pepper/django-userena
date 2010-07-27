.. _commands:

Commands.
=========

Userena currently comes with two commands. ``cleanexpired`` for cleaning out
the expired users and ``notifyexpired`` for notifying the almost expired users.

Clean expired
--------------

Search for users that still haven't verified their e-mail address after
``USERENA_ACTIVATION_DAYS`` and delete them. Run by ::

    ./manage.py cleanexpired

Notify expired 
---------------

Search for users which account is almost expired and send them a notification
email. Run by ::

    ./manage.py notifyexpired


