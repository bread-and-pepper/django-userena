.. _faq:

F.A.Q
=====

I get a "``Permission matching query does not exist``" exception
----------------------------------------------------------------

Sometimes Django decides not to install the default permissions for a model
and thus the ``change_profile`` permission goes missing. To fix this, run the
``check_permissions`` in :ref:`commands`. This checks all permissions and adds
those that are missing.

<ProfileModel> is already registered exception
----------------------------------------------

Userena already registered your profile model for you. If you want to
customize the profile model, you can do so by registering your profile as
follows::

    # Unregister userena's
    admin.site.unregister(YOUR_PROFILE_MODEL)
    
    # Register your own admin class and attach it to the model
    admin.site.register(YOUR_PROFILE_MODEL, YOUR_PROFILE_ADMIN)
