.. _faq:

F.A.Q
=====

I get a "``Permission matching query does not exist``" exception
----------------------------------------------------------------

Sometimes Django decides not to install the default permissions for a model
and thus the ``change_profile`` permission goes missing. To fix this, run the
``check_permissions`` in :ref:`commands`. This checks all permissions and adds
those that are missing.
