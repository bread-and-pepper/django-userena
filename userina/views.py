from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate

from userina.forms import SignupForm
from userina.models import Account

def verify(request, verification_key):
    """ Verify an account through an verification key """
    pass

def signin(request):
    """
    Signin using your e-mail or username and password. You can also select to
    be rememebered for ``USERINA_REMEMBER_DAYS``.

    """
    pass

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
def detail(request):
    """ View your own account """
    pass
