.. _installation:

Settings
========

Userena comes with a few settings that enables you to tweak the user experience
for you users. There are also a few Django settings that are relevant for
Userena.

Userena settings
----------------

USERENA_ACTIVATION_DAYS
~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``7`` (integer)

A integer which stands for the amount of days a user has to activate their
account. The user will be deleted when they still haven't activated their
account after these amount of days by running the ``cleanexpired``
:ref:`command <commands>`.

USERENA_ACTIVATION_NOTIFY
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``True`` (boolean)

A boolean that turns on/of the sending of a notification when
``USERENA_ACTIVATION_NOTIFY_DAYS`` away the activation of the user will
expire and the user will be deleted.

USERENA_ACTIVATION_NOTIFY_DAYS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``2`` (integer)

The amount of days, before the expiration of an account, that a notification
get's send out. Warning the user of his coming demise.

USERENA_VERIFIED
~~~~~~~~~~~~~~~~
Default: ``ALREADY_VERIFIED`` (string)

This value will be inserted into ``Account.activation_key`` if a key gets
used successfully.

USERENA_REMEMBER_ME_DAYS
~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``(gettext('a month'), 30))`` (tuple)

A tuple containing a string and an integer which stand for the amount of days a
user can choose to be remembered by your project. The string is the human
readable version that gets displayed in the form. The integer stands for the
amount of days that this string represents.

USERENA_FORBIDDEN_USERNAMES
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``('signup', 'signout', 'signin', 'activate', 'me', 'password')`` (tuple)

A tuple containing the names which cannot be used as username in the signup
form.

.. _userena-mugshot-gravatar:

USERENA_MUGSHOT_GRAVATAR
~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``True`` (boolean)

A boolean defining if mugshots should fallback to `Gravatar
<http://en.gravatar.com/>`_ service when no mugshot is uploaded by the user.

USERENA_MUGSHOT_DEFAULT
~~~~~~~~~~~~~~~~~~~~~~~
Default: ``identicon`` (string)

A string for the default image used when no mugshot is found. This can be
either a URI to an image or if :ref:`userena-mugshot-gravatar` is
``True`` one of the following options:

``404``
    Do not load any image if none is associated with the email hash, instead
    return an HTTP 404 (File Not Found) response.

``mm``
    Mystery-man, a simple, cartoon-style silhouetted outline of a person (does
    not vary by email hash).

``identicon``
    A geometric pattern based on an email hash.

``monsterid``
    A generated 'monster' with different colors, faces, etc.

``wavatar``
    Generated faces with differing features and backgrounds

USERENA_MUGSHOT_SIZE
~~~~~~~~~~~~~~~~~~~~
Default: ``80`` (int)

Integer defining the size (in pixels) of the sides of the mugshot image.

Django settings
---------------

LOGIN_REDIRECT_URL
~~~~~~~~~~~~~~~~~~
Default: ``/accounts/profile/`` (string)

The URL where requests are redirected after login when the contrib.auth.login
view gets no next parameter. 

In userena this URL normally would be ``/accounts/me/``.

LOGIN_URL
~~~~~~~~~
Default: ``/accounts/login/`` (string)

The URL where requests are redirected for login, especially when using the
login_required() decorator.

In userena this URL normally would be ``/accounts/signin/``.

LOGOUT_URL
~~~~~~~~~~
Default: ``/accounts/logout/`` (string)
LOGIN_URL counterpart.

In userena this URL normally would be ``/accounts/signout/``.
