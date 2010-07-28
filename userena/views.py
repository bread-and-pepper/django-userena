from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404

from userena.forms import SignupForm, AuthenticationForm, ChangeEmailForm
from userena.models import Account
from userena.decorators import secure_required
from userena.backends import UserenaAuthenticationBackend
from userena.utils import signin_redirect
from userena import settings as userena_settings

@secure_required
def activate(request, activation_key, template_name='userena/activation.html'):
    """ Activate a user through an activation key """
    account = Account.objects.activate_user(activation_key)
    if account:
        return redirect(reverse('userena_activation_complete'))
    else:
        return direct_to_template(request,
                                  template_name)

@secure_required
def signin(request, auth_form=AuthenticationForm, template_name='userena/signin_form.html',
           redirect_field_name=REDIRECT_FIELD_NAME, redirect_signin_function=signin_redirect):
    """
    Signin using your e-mail or username and password. You can also select to
    be remembered for ``USERENA_REMEMBER_DAYS``.

    **Keyword arguments**

    ``auth_form``
        The form to use for signing the user in. Defaults to the
        ``AuthenticationForm`` supplied by userena.

    ``template_name``
        A custom template to use. Defaults to ``userena/signin_form.html``.

    ``redirect_field_name``
        The field name which contains the value for a redirect to the
        successing page. Defaults to ``next`` and is set in
        ``REDIRECT_FIELD_NAME``.

    ``redirect_signin_function``
        A function which handles the redirect. This functions gets the value of
        ``REDIRECT_FIELD_NAME`` and the ``User`` who has logged in. It must
        return a string which specifies the URI to redirect to.

    """
    form = auth_form

    if request.method == 'POST':
        form = auth_form(data=request.POST)
        if form.is_valid():
            identification, password, remember_me = (form.cleaned_data['identification'],
                                                     form.cleaned_data['password'],
                                                     form.cleaned_data['remember_me'])
            user = authenticate(identification=identification,
                                password=password)
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 3600)
                else: request.session.set_expiry(0)

                # Whereto now?
                requested_redirect = request.REQUEST.get(redirect_field_name, None)
                redirect_to = redirect_signin_function(requested_redirect,
                                                       user)
                redirect_to = request.REQUEST.get(redirect_field_name,
                                                  userena_settings.USERENA_SIGNIN_REDIRECT_URL % {'username': user.username})
                return redirect(redirect_to)
            else:
                return redirect(reverse('userena_disabled'))

    return direct_to_template(request,
                              template_name,
                              extra_context={'form': form})

@secure_required
def signup(request, template_name='userena/signup_form.html'):
    """ Signup a user """
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            username, email, password = (form.cleaned_data['username'],
                                         form.cleaned_data['email'],
                                         form.cleaned_data['password1'])
            # Create new user
            new_account = Account.objects.create_inactive_user(username, email, password)

            # Login the user
            new_user = authenticate(username=username,
                                    password=password)
            return redirect(reverse('userena_signup_complete'))

    return direct_to_template(request,
                              template_name,
                              extra_context={'form': form})

@secure_required
@login_required
def email_change(request, username, template_name='userena/email_form.html'):
    """ Change your e-mail address. Doing this requires a new verification. """
    form = ChangeEmailForm(request.user)
    if request.method == 'POST':
        form = ChangeEmailForm(request.user,
                               data=request.POST)

        if form.is_valid():
            new_email = form.cleaned_data['email']
            # Change the e-mail address
            request.user.account.change_email(new_email)
            return redirect(reverse('userena_email_complete'))

    return direct_to_template(request,
                              template_name,
                              extra_context={'form': form})

def detail(request, username, template_name='userena/detail.html', edit=False):
    """ View the account of others. """
    account = get_object_or_404(Account,
                                user__username__iexact=username)
    return direct_to_template(request,
                              template_name,
                              extra_context={'account': account})

def list(request):
    """ Returns a list of all the users """
    pass
