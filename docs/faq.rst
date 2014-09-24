.. _faq:

F.A.Q
=====

I get a "``Permission matching query does not exist``" exception
----------------------------------------------------------------

Sometimes Django decides not to install the default permissions for a model
and thus the ``change_profile`` permission goes missing. To fix this, run the
``check_permissions`` in :ref:`commands`. This checks all permissions and adds
those that are missing.

I get a "``Site matching query does not exist.``" exception
-----------------------------------------------------------

This means that your settings.SITE_ID value is incorrect. See the instructions
on SITE_ID in the [Installation section](http://docs.django-userena.org/en/latest/installation.html).


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

Can I still add users manually?
-------------------------------           
Yes, but Userena requires there to be a `UserenaSignup` object for every
registered user. If it's not there, you could receive the following error:

.. code-block:: python

                Exception Type: DoesNotExist at /accounts/mynewuser/email/

So, whenever you are manually creating a user (outside of Userena), don't
forget to also create a `UserenaSignup` object.

How can I have multiple profiles per user?
------------------------------------------

One way to do this is by overriding the `save` method on `SignupForm` with
your own form, extending userena's form and supply this form with to the
signup view. For example:

.. code-block:: python

    def save(self):
        """ My extra profile """
        # Let userena do it's thing
        user = super(SignupForm, self).save()

        # You do all the logic needed for your own extra profile
        custom_profile = ExtraProfile()
        custom_profile.extra_field = self.cleaned_data['field']
        custom_profile.save()

        # Always return the new user
        return user

Important to note here is that you should always return the newly created
`User` object. This is something that userena expects. Userena will take care
of creating the user and the "standard" profile.

Don't forget to supply your own form to the signup view by overriding the URL
in your `urls.py`:

.. code-block:: python

     (r'^accounts/signup/$',
      'userena.views.signup',
      {'signup_form': SignupExtraProfileForm}),

How do I add extra fields to forms?
-----------------------------------

This is done by overriding the default templates. A demo tells more than a
thousand words. So here's how you add the first and last name to the signup
form. First you override the signup form and add the fields.

.. code-block:: python

    from django import forms
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

            # Get the profile, the `save` method above creates a profile for each
            # user because it calls the manager method `create_user`.
            # See: https://github.com/bread-and-pepper/django-userena/blob/master/userena/managers.py#L65
            user_profile = new_user.get_profile()

            user_profile.first_name = self.cleaned_data['first_name']
            user_profile.last_name = self.cleaned_data['last_name']
            user_profile.save()

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
