.. _umessages:

uMessages
=========

Userena's umesagges supplies you with iPhone like messaging system for your
users.


Installation
------------

You install it by adding ``userena.contrib.umessages`` to your
``INSTALLED_APPS`` setting. You also need to add it to your urlconf. For
example::

    (r'^messages/', include('userena.contrib.umessages.urls')),

A ``syncdb`` later and you have a great messaging system for in your
application.

.. toctree::
   :maxdepth: 2
   
   api/index
