from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate

from userena import settings as userena_settings
from userena.models import Account

attrs_dict = {'class': 'required'}

class SignupForm(forms.Form):
    """
    Form for creating a new user account.

    Validates that the requested username and e-mail is not already in use.
    Also requires the password to be entered twice. A TOS is also required to be seen.

    """
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _('Username must contain only letters, numbers and underscores.')})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password (again)"))

    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _('You must agree to the terms to register.')})

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already in use.
        Also validates that the username is not listed in
        ``USERENA_FORBIDDEN_USERNAMES`` list.

        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            pass
        else:
            raise forms.ValidationError(_('This username is already taken.'))
        if self.cleaned_data['username'].lower() in userena_settings.USERENA_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_('This username is not allowed.'))
        return self.cleaned_data['username']

    def clean_email(self):
        """ Validate that the e-mail address is unique """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_('This email address is already in use. Please supply a different email address.'))
        return self.cleaned_data['email']

    def clean(self):
        """
        Verify that the values entered into the two password fields match. Note
        that an error here will end up in ``non_field_errors()`` because it
        doesn't apply to a single field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return self.cleaned_data

class AuthenticationForm(forms.Form):
    """
    A custom ``AuthenticationForm`` where the identification can be a e-mail
    address or username.

    """
    identification = forms.CharField(label=_("Email or username"),
                                     widget=forms.TextInput(attrs=attrs_dict),
                                     max_length=75,
                                     error_messages={'required': _('Either supply us with your e-mail address or username.')})
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(attrs=attrs_dict, render_value=False))
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                                     required=False,
                                     label=_(u'Remember me for %(days)s' % {'days': userena_settings.USERENA_REMEMBER_ME_DAYS[0]}))

    def clean(self):
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            user = authenticate(identification=identification, password=password)
            if user is None:
                raise forms.ValidationError(_("Please enter a correct username or email and password. Note that both fields are case-sensitive."))
        return self.cleaned_data

class ChangeEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("New email address"))

    def __init__(self, user, *args, **kwargs):
        """
        The current ``user`` needs to be supplied with this form so that we can
        check if the e-mail address is still free.

        """
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        if not isinstance(user, User):
            raise TypeError, "user must be an instance of User"
        else: self.user = user

        self.fields['email'].help_text = _('Your current email is %(email)s' % \
                                           {'email': user.email})

    def clean_email(self):
        """ Validate that the e-mail address is not already registered with another user """
        if self.cleaned_data['email'].lower() == self.user.email:
            raise forms.ValidationError(_('Your already known under this email address.'))
        if User.objects.filter(email__iexact=self.cleaned_data['email']).exclude(email__iexact=self.user.email):
            raise forms.ValidationError(_('This email address is already in use. Please supply a different email address.'))
        return self.cleaned_data['email']

class AccountEditForm(forms.ModelForm):
    """ Edit your account form. """
    class Meta:
        model = Account
        # Exclude the fields used for managing the accounts.
        exclude = ('user', 'last_active', 'activation_key', 'activation_key_created',
                   'activation_notification_send', 'email_new', 'email_verification_key')
