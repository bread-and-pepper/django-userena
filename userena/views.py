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
def activate(request, activation_key,
             template_name='userena/activation_fail.html',
             success_url=None, extra_context={}):
    """
    Activate a user with an activation key.

    **Arguments**

    ``activation_key``
        A SHA1 string of 40 characters long. A SHA1 is always 160bit long, with
        4 bits per character this makes it --160/4-- 40 characters long.

    **Keyword arguments**

    ``template_name``
        The template that is used when the ``activation_key`` is invalid and
        the activation failes. Defaults to ``userena/activation_fail.html``.

    ``success_url``
        A string with the URI which the user should be redirected to after a
        succesfull activation. If not specified, will direct to
        ``userena_activation_complete`` view.

    ``extra_context``
        Dictionary containing variables which could be added to the template
        context. Default to an empty dictionary.

    """
    account = Account.objects.activate_user(activation_key)
    if account:
        if success_url: redirect_to = success_url
        else: redirect_to = reverse('userena_activation_complete')
        return redirect(redirect_to)
    else: return direct_to_template(request,
                                    template_name,
                                    extra_context=extra_context)

@secure_required
def verify(request, verification_key):
    pass

@secure_required
def signin(request, auth_form=AuthenticationForm,
           template_name='userena/signin_form.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_signin_function=signin_redirect):
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
                return redirect(redirect_to)
            else:
                return redirect(reverse('userena_disabled'))

    return direct_to_template(request,
                              template_name,
                              extra_context={'form': form})

@secure_required
def signup(request, signup_form=SignupForm,
           template_name='userena/signup_form.html', success_url=None,
           extra_context={}):
    """
    Signup a user requiring them to supply a username, email and password.

    **Keyword arguments**

    ``signup_form``
        The form that will be used to sign a user. Defaults to userena's
        ``forms.SignupForm``.

    ``template_name``
        The template that will be used to display the signup form. Defaults to
        ``userena/signup_form.html``.

    ``success_url``
        String containing the URI which should be redirected to after a
        successfull signup. If not supplied will redirect to
        ``userena_signup_complete`` view.

    ``extra_context``
        Dictionary containing variables which are added to the template
        context. Defaults to a dictionary with a ``form`` key containing the
        ``signup_form``.

    **Context**

    ``form``
        The signup form supplied by ``signup_form``.

    """
    form = signup_form()

    if request.method == 'POST':
        form = signup_form(data=request.POST)
        if form.is_valid():
            username, email, password = (form.cleaned_data['username'],
                                         form.cleaned_data['email'],
                                         form.cleaned_data['password1'])

            # Create new user
            new_account = Account.objects.create_inactive_user(username, email, password)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_signup_complete')
            return redirect(redirect_to)

    extra_context['form'] = form
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

@secure_required
@login_required
def email_change(request, username, form=ChangeEmailForm,
                 template_name='userena/email_form.html', success_url=None,
                 extra_context={}):
    """
    Change e-mail address

    **Arguments**

    ``username``
        The username which specifies the current account.

    **Keyword arguments**

    ``form``
        The form that will be used to change the email address. Defaults to
        ``ChangeEmailForm`` supplied by userena.

    ``template_name``
        Template to be used to display the email form. Defaults to
        ``userena/email_form.html``.

    ``success_url``
        If the form is valid the user will get redirected to ``success_url``.
        When not suplied will redirect to ``userena_email_complete`` view.

    ``extra_context``
        Dictionary containing extra variables that can be used to render the
        template. The ``form`` key is always the form supplied by the keyword
        argument ``form``.

    **Context**

    ``form``
        The email change form supplied by ``form``.

    **Todo**

    Need to have per-object permissions, which enables users with the correct
    permissions to alter the e-mail address of others.

    """
    user = get_object_or_404(User, username__iexact=username)
    form = ChangeEmailForm(user)

    if request.method == 'POST':
        form = ChangeEmailForm(user,
                               data=request.POST)

        if form.is_valid():
            new_email = form.cleaned_data['email']
            # Change the e-mail address
            user.account.change_email(new_email)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_email_complete',
                                        kwargs={'username': user.username})
            return redirect(redirect_to)

    extra_context['form'] = form
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

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
