.. _installation:

Installation.
=============

Before install django-userina, you'll need to have a copy of `Django
<http://www.djangoproject.com>`_ 1.2 or newer installed.

For further information, consult the `Django download page
<http://www.djangoproject.com/download/>`_, which offers convenient packaged
downloads and installation instructions.

Installing django-userina.
--------------------------

You can install django-userina automagicly with ``easy_install`` or ``pip``. Or
manually placing it on on your ``PYTHON_PATH``.

I'm using `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ to have an
isolated python environment. This way it's possible to create a tailored
environment for each project.

Automatic installation with easy_install.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automatic install with `easy_install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_. You'll first have to
clone the Git repository from Github. Then you can direct easy_install to the
``setup.py`` file. For ex.::

    git clone git://github.com/bread-and-pepper/django-userina.git
    cd django-userina
    easy_install setup.py


Automatic installation with pip.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can tell `pip <http://pip.openplans.org/>`_ to install django-userina by
supplying it with the git repository on Github. Do this by typing the following
in your terminal::

    pip install -e git+git://github.com/bread-and-pepper/django-userina.git#egg=userina


Manual installation with git.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Required settings
-----------------

Begin by adding ``userina`` to the ``INSTALLED_APPS`` setting of your project
and adding ``UserinaAuthenticationBackend`` at the top of
``AUTHENTICATION_BACKENDS``. If you only want Django's default backend and that
of userina you will get the following::

    AUTHENTICATION_BACKENDS = (
        'userina.UserinaAuthenticationBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

The URI's
~~~~~~~~~

Userina has a ``URLconf`` which set's all the url's and views for you. This
should be included in your projects root ``URLconf``.

For example, to place the URIs under the prefix ``/accounts/``, you could add
the following to your project's root ``URLconf``::

    (r'^accounts/', include('userina.urls')),

This should have you a working accounts application for your project. See the
:ref:`settings <settings>` and :ref:`templates <templates>` for further
configuration options.
