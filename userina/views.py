from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

from userina.forms import SignupForm, AuthenticationForm
from userina.models import Account
from userina import settings as userina_settings

def verify(request, verification_key):
    """ Verify an account through an verification key """
    pass

def signin(request, template_name='userina/signin_form.html',
           redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Signin using your e-mail or username and password. You can also select to
    be remembered for ``USERINA_REMEMBER_DAYS``.

    """
    form = AuthenticationForm()
    redirect_to = request.REQUEST.get(redirect_field_name,
                                      settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            identification, password, remember_me = (form.cleaned_data['identification'],
                                                     form.cleaned_data['password'],
                                                     form.cleaned_data['remember_me'])
            user = authenticate(identification=identification,
                                password=password)
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(userina_settings.USERINA_REMEMBER_ME_DAYS[1] * 3600)
                else: request.session.set_expiry(0)
                return redirect(redirect_to)
            else:
                return redirect(reverse('userina_disabled'))

    return direct_to_template(request,
                              template_name,
                              extra_context={'form': form})

@login_required
def signout(request, redirect=None):
    """ Signout a user and redirect them to the ``redirect``. """
    pass

def signup(request, template_name='userina/signup_form.html'):
    """ Signup a user """
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            username, email, password = (form.cleaned_data['username'],
                                         form.cleaned_data['email'],
                                         form.cleaned_data['password1'])
            # Create new user
            new_account = Account.objects.create_user(username, email, password)

            # Login the user
            new_user = authenticate(username=username,
                                    password=password)
            return redirect(reverse('userina_signup_complete'))

    return direct_to_template(request,
                              template_name,
                              extra_context={'form': form})

def password_reset(request):
    """
    Resets your password by sending you a new URI which enables you to choose a
    new password

    """
    pass

def password_reset_confirm(request, token):
    """
    Let's you choose a new password if your ``token`` is correct.

    """
    pass

@login_required
def password_change(request):
    """ Change your password """
    pass

@login_required
def detail(request, template_name='userina/detail.html'):
    """ View your own account """
    return direct_to_template(request,
                              template_name,
                              extra_context={})
