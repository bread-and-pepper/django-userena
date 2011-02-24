.. _commands:

Commands.
=========

Userena currently comes with two commands. ``cleanexpired`` for cleaning out
the expired users and ``check_permissions`` for checking the correct
permissions needed by userena.

Clean expired
--------------

Search for users that still haven't verified their e-mail address after
``USERENA_ACTIVATION_DAYS`` and delete them. Run by ::

    ./manage.py clean_expired

Check permissions
-----------------

This command shouldn't be run as a cronjob. This is only for emergency
situations when some permissions are not correctly set for users. For example
when userena get's implemented in an already existing project. Run by ::

    ./manage.py check_permissions
