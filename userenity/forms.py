from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from userenity.models import Account

class AccountForm(forms.ModelForm):
    """
    A form that implements all the fields for a user.

    We don't want to edit a seperate user and account form.

    """
    username = forms.RegexField(label=_('Username'), max_length=30, regex=r'^[\w.@+-]+$',
        help_text = _('Required. 30 characters or fewer. Letters, digits and @.+-_ only.'),
        error_messages = {'invalid': _('This value may contain only letters, numbers and @/./+/-/_ characters.')})
    email = forms.EmailField(label=_('Email'))
    password_1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput, required=False)
    password_2 = forms.CharField(label=_('Password again'), widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('Last name'), max_length=30, required=False)

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        try:
            self.current_user = self.instance.user
        except User.DoesNotExist:
            self.current_user = None
        else:
            self.fields['username'].initial = self.current_user.username
            self.fields['email'].initial = self.current_user.email
            self.fields['first_name'].initial = self.current_user.first_name
            self.fields['last_name'].initial = self.current_user.last_name

    class Meta:
        model = Account
        fields = ['username','email', 'password_1', 'password_2', 'first_name', 'last_name', 'mugshot', 'gender', 'birth_date', 'website']

    def clean_username(self):
        username = self.cleaned_data['username']
        # Only check the username if the user is a new one
        if not self.current_user:
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(_('A user with that username already exists.'))
        return username

    def clean_password_1(self):
        # Check passwords for new user
        if self.current_user:
            if 'password_1' in self.cleaned_data and 'password_2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError(_('Passwords are not equal'))
            else:
                raise forms.ValidationError(_('Passwords are required for a new user'))
        # Existing user
        else:
            if 'password_1' in self.cleaned_data and 'password_2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError(_('Passwords are not equal'))
        return self.cleaned_data['password_1']

    def save(self, commit=True):
        """
        Update the account and user.

        """
        if self.current_user: # Update the current user
            self.current_user.email = self.cleaned_data['email']
            self.current_user.save()

        else: # Create a new user
            user = User.objects.create_user(self.cleaned_data['username'],
                                            self.cleaned_data['email'],
                                            self.cleaned_data['password_1'])
            self.user = user

            # TODO: Bit ugly to save a item multiple times.
            account = super(AccountForm, self).save(commit=False)
            account.user = user
            account.save()

        return account
