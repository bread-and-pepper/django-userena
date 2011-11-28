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
follows:

.. code-block:: python

    # Unregister userena's
    admin.site.unregister(YOUR_PROFILE_MODEL)
    
    # Register your own admin class and attach it to the model
    admin.site.register(YOUR_PROFILE_MODEL, YOUR_PROFILE_ADMIN)

How do I add extra fields to forms?
-----------------------------------

This is done by overriding the default templates. A demo tells more than a
thousand words. So here's how you add the first and last name to the signup
form. First you override the signup form and add the fields.

.. code-block:: python

    django import forms
    from django.utils.translation import ugettext_lazy as _

    from userena.forms import SignupForm

    class SignupFormExtra(SignupForm):
        """ 
        A form to demonstrate how to add extra fields to the signup form, in this
        case adding the first and last name.


        """
        first_name = forms.CharField(label=_(u'First name'),
                                     max_length=30,
                                     required=False)

        last_name = forms.CharField(label=_(u'Last name'),
                                    max_length=30,
                                    required=False)

        def __init__(self, *args, **kw):
            """

            A bit of hackery to get the first name and last name at the top of the
            form instead at the end.

            """
            super(SignupFormExtra, self).__init__(*args, **kw)
            # Put the first and last name at the top
            new_order = self.fields.keyOrder[:-2]
            new_order.insert(0, 'first_name')
            new_order.insert(1, 'last_name')
            self.fields.keyOrder = new_order

        def save(self):
            """ 
            Override the save method to save the first and last name to the user
            field.

            """
            # First save the parent form and get the user.
            new_user = super(SignupFormExtra, self).save()

            new_user.first_name = self.cleaned_data['first_name']
            new_user.last_name = self.cleaned_data['last_name']
            new_user.save()

            # Userena expects to get the new user from this form, so return the new
            # user.
            return new_user

Finally, to use this form instead of our own, override the default URI by
placing a new URI above it.

.. code-block:: python

     (r'^accounts/signup/$',
      'userena.views.signup',
      {'signup_form': SignupFormExtra}),

That's all there is to it!
