.. _installation:

Installation.
=============

Before install django-userena, you'll need to have a copy of `Django
<http://www.djangoproject.com>`_ 1.2 or newer installed.

For further information, consult the `Django download page
<http://www.djangoproject.com/download/>`_, which offers convenient packaged
downloads and installation instructions.

Installing django-userena.
--------------------------

You can install django-userena automagicly with ``easy_install`` or ``pip``. Or
manually placing it on on your ``PYTHON_PATH``.

I'm using `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ to have an
isolated python environment. This way it's possible to create a tailored
environment for each project.

Automatic installation with easy_install.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automatic install with `easy_install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_. All you have to do is
run the following command::

    easy_install django-userena

Manual installation with easy_install.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Clone the Git repository from Github. Then you can direct easy_install to the
``setup.py`` file. For ex.::

    git clone git://github.com/bread-and-pepper/django-userena.git
    cd django-userena
    easy_install setup.py


Automatic installation of development version with pip.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can tell `pip <http://pip.openplans.org/>`_ to install django-userena by
supplying it with the git repository on Github. Do this by typing the following
in your terminal::

    pip install -e git+git://github.com/bread-and-pepper/django-userena.git#egg=userena


Manual installation of development version with git.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone userena with::
    
    git clone git://github.com/bread-and-pepper/django-userena.git

You now have a directory ``django-userena`` which contains the ``userena``
application. You can add userena to your ``$PYTHONPATH`` by symlinking it. For
example::

    cd YOUR_PYTHON_PATH
    ln -s ~/src/django-userena/userena userena

Now userena is available to your project.

Required settings
-----------------

You need to make some changes Django settings if you want to use Userena in
your project. This means modifying ``AUTHENTICATION_BACKENDS``,
``INSTALLED_APPS`` and optionally ``MIDDLEWARE_CLASSES``.

Begin by adding ``userena``, ``guardian`` and ``easy_thumbnails`` to the
``INSTALLED_APPS`` settings of your project.

Next add :class:``UserenaAuthenticationBackend`` and :class:``ObjectPermissionBackend``, from
django-guardian, at the top of ``AUTHENTICATION_BACKENDS``. If you only have
Django's default backend, adding django-guardian and that of userena will get
the following::

    AUTHENTICATION_BACKENDS = (
        'userena.UserenaAuthenticationBackend',
        'guardian.backends.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

Profiles
~~~~~~~~

Userena needs you to define the profile that is used by supplying Django's
``AUTH_PROFILE_MODULE`` setting. Userena supplies the following two base
profiles for you that you should use for your own profile model by inheriting
from them:

    ``UserenaBaseProfile``
        Basic profile that supplies your user with mugshots and the necessary
        fields for privacy settings.

    ``UserenaLanguageBaseProfile``
        Adds an extra field that let's the user define it's preferred language
        after logging in to your site.

**IMPORTANT**: The above profiles are ``abstract`` models. This means that you
cannot use them directly in ``AUTH_PROFILE_MODULE`` but you must create your
own profile model which inherits from one of the above models. For ex::

    from userena.models import UserenaBaseProfile
    
    class MyProfile(UserenaBaseProfile):
        favourite_snack = models.CharField(_('favourite snack'),
                                           max_length=5)

If you want the user have the ability to choose their default language in their
profile, you must add ``UserenaLocaleMiddleware`` at the end of
``MIDDLEWARE_CLASSES`` in your Django settings. This does require a profile
model which has a language field. You can use the
``UserenaLanguageBaseProfile`` class of userena that does this for you.

The URI's
~~~~~~~~~

Userena has a ``URLconf`` which set's all the url's and views for you. This
should be included in your projects root ``URLconf``.

For example, to place the URIs under the prefix ``/accounts/``, you could add
the following to your project's root ``URLconf``::

    (r'^accounts/', include('userena.urls')),

This should have you a working accounts application for your project. See the
:ref:`settings <settings>` and :ref:`templates <templates>` for further
configuration options.

Required settings
~~~~~~~~~~~~~~~~~

Django-guardian requires you to set the ``ANONYMOUS_USER_ID`` setting. I always
set this to ``-1``. As noted before, you are also required to set the
``AUTH_PROFILE_MODULE`` to your custom defined profile.

To integrate Django with userena you should alter the following three settings
to reflect the URI you have chosen for userena. For example, if userena lives
under ``accounts``::

    LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
    LOGIN_URL = '/accounts/signin/'
    LOGOUT_URL = '/accounts/signout/'

The above should supply you with a fully functional account management app. for
your project. You can look into the next chapter to fully customize userena to
your likings.

.. _Github: https://github.com/lukaszb/django-guardian
