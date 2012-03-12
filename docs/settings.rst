.. _settings:

Settings
========

Userena comes with a few settings that enables you to tweak the user experience
for you users. There are also a few Django settings that are relevant for
Userena.

Userena settings
----------------

USERENA_SIGNIN_REDIRECT_URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default ``/accounts/%(username)s/'`` (string)

A string which defines the URI where the user will be redirected to after
signin.

USERENA_ACTIVATION_REQUIRED
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``True`` (integer)

Boolean that defines if a activation is required when creating a new user.

USERENA_ACTIVATION_DAYS
~~~~~~~~~~~~~~~~~~~~~~~
Default: ``7`` (integer)

A integer which stands for the amount of days a user has to activate their
account. The user will be deleted when they still haven't activated their
account after these amount of days by running the ``cleanexpired``
:ref:`command <commands>`.

USERENA_ACTIVATION_NOTIFY
~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``True`` (boolean)

A boolean that turns on/off the sending of a notification when
``USERENA_ACTIVATION_NOTIFY_DAYS`` away the activation of the user will
expire and the user will be deleted.

USERENA_ACTIVATION_NOTIFY_DAYS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``2`` (integer)

The amount of days, before the expiration of an account, that a notification
get's send out. Warning the user of his coming demise.

USERENA_ACTIVATED
~~~~~~~~~~~~~~~~~
Default: ``ALREADY_ACTIVATED`` (string)

String that defines the value that the ``activation_key`` will be set to after
a successful signup.

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

USERENA_MUGSHOT_GRAVATAR_SECURE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``USERENA_USE_HTTPS`` (boolean)

A boolean defining if the secure URI of Gravatar is used. Defaults to
the same value as ``USERENA_USE_HTTPS``.

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

USERENA_MUGSHOT_PATH
~~~~~~~~~~~~~~~~~~~~
Default: ``mugshots/`` (string)

The default path that the mugshots will be saved to. Is appended to the
``MEDIA_PATH`` in your Django settings.

USERENA_USE_HTTPS
~~~~~~~~~~~~~~~~~
Default: ``False`` (boolean)

Boolean that defines if you have a secure version of your website. If so,
userena will redirect sensitive URI's to the secure protocol.

USERENA_DEFAULT_PRIVACY
~~~~~~~~~~~~~~~~~~~~~~~
Default: ``registered`` (string)

Defines the default privacy value for a newly registered user. There are three
options:

``closed``
    Only the owner of the profile can view their profile.

``registered``
    All registered users can view their profile.

``open``
    All users (registered and anonymous) can view their profile.

USERENA_PROFILE_DETAIL_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``userena/profile_detail.html`` (string)

Template to use for rendering user profiles. This allows you to specify a
template in your own project which extends ``userena/profile_detail.html``.

USERENA_DISABLE_PROFILE_LIST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``False`` (boolean)

Boolean value that defines if the ``profile_list`` view is enabled within the
project. If so, users can view a list of different profiles.

USERENA_USE_MESSAGES
~~~~~~~~~~~~~~~~~~~~
Default: ``True`` (boolean)

Boolean value that defines if userena should use the django messages framework
to notify the user of any changes.

USERENA_LANGUAGE_FIELD
~~~~~~~~~~~~~~~~~~~~~~
Default: ``language`` (string)

The language field that is used in the custom profile to define the preferred
language of the user.

USERENA_WITHOUT_USERNAMES
~~~~~~~~~~~~~~~~~~~~~~~~~
Default: ``False`` (boolean)

Defines if usernames are used within userena. Currently it's often for the
users convenience that only an email is used for identification. With this
setting you get just that.

USERENA_HIDE_EMAIL
~~~~~~~~~~~~~~~~~~
Default: ``False`` (boolean)

Prevents email addresses from being displayed to other users if set to `
`True``.

Django settings
---------------

LOGIN_URL
~~~~~~~~~
Default: ``/accounts/login/`` (string)

The URL where requests are redirected for login, especially when using the
login_required() decorator.

In userena this URI normally would be ``/accounts/signin/``.

LOGOUT_URL
~~~~~~~~~~
Default: ``/accounts/logout/`` (string)
LOGIN_URL counterpart.

In userena this URI normally would be ``/accounts/signout/``.

LOGIN_REDIRECT_URL
~~~~~~~~~~~~~~~~~~
Default: ``/accounts/profile/``

In userena this URI should point to the profile of the user. Thus a string of
``/accounts/%(username)s/`` is best.

AUTH_PROFILE_MODULE
~~~~~~~~~~~~~~~~~~~
Default: ``not defined``

This should point to the model that is your custom made profile.
