from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from django.contrib import messages
from django.utils.translation import ugettext as _

from userena.forms import SignupForm, AuthenticationForm, ChangeEmailForm, AccountEditForm
from userena.models import Account
from userena.decorators import secure_required
from userena.backends import UserenaAuthenticationBackend
from userena.utils import signin_redirect
from userena import settings as userena_settings

@secure_required
def activate(request, activation_key,
             template_name='userena/activation_fail.html',
             success_url=None, extra_context=None):
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
    user = Account.objects.activate_user(activation_key)
    if user:
        if success_url: redirect_to = success_url
        else: redirect_to = reverse('userena_activation_complete')
        return redirect(redirect_to)
    else:
        if not extra_context: extra_context = dict()
        return direct_to_template(request,
                                  template_name,
                                  extra_context=extra_context)

@secure_required
def verify(request, verification_key,
           template_name='userena/verification_fail.html', success_url=None,
           extra_context=None):
    """
    Verify your email address with a verification key.

    **Arguments**

    ``verification_key``
        A SHA1 representing the verification key used to verify a new email
        address.

    **Keyword arguments**

    ``template_name``
        Template which should be rendered when verification fails. When
        verification is succesfull, no template is needed because the user will
        be redirected.

    ``success_url``
        The URL which is redirected to after a succesfull verification.
        Supplied argument must be able to be rendered by ``reverse`` function.

    ``extra_context``
        Dictionary of variables that are passed on to the template supplied by
        ``template_name``.

    """
    account = Account.objects.verify_email(verification_key)
    if account:
        if success_url: redirect_to = success_url
        else: redirect_to = reverse('userena_verification_complete')
        return redirect(redirect_to)
    else:
        if not extra_context: extra_context = dict()
        return direct_to_template(request,
                                    template_name,
                                    extra_context=extra_context)


@secure_required
def signin(request, auth_form=AuthenticationForm,
           template_name='userena/signin_form.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_signin_function=signin_redirect, extra_context=None):
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

    ``extra_context``
        A dictionary containing extra variables that should be passed to the
        rendered template. The ``form`` key is always the ``auth_form``.

    **Context**

    ``form``
        Variable containing the form used for authentication.

    """
    form = auth_form

    if request.method == 'POST':
        form = auth_form(request.POST, request.FILES)
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

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    return direct_to_template(request,
                              template_name,
                              extra_context={'form': form})

@secure_required
def signup(request, signup_form=SignupForm,
           template_name='userena/signup_form.html', success_url=None,
           extra_context=None):
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
        form = signup_form(request.POST, request.FILES)
        if form.is_valid():
            username, email, password = (form.cleaned_data['username'],
                                         form.cleaned_data['email'],
                                         form.cleaned_data['password1'])

            # Create new user
            new_account = Account.objects.create_inactive_user(username, email, password)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_signup_complete')
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

@secure_required
@login_required
def email_change(request, username, form=ChangeEmailForm,
                 template_name='userena/email_form.html', success_url=None,
                 extra_context=None):
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
        argument ``form`` and the ``user`` key by the user whose email address
        is to be changed.

    **Context**

    ``form``
        The email change form supplied by ``form``.

    ``user``
        The user whose email address is about to be changed.

    **Todo**

    Need to have per-object permissions, which enables users with the correct
    permissions to alter the e-mail address of others.

    """
    user = get_object_or_404(User, username__iexact=username)
    form = ChangeEmailForm(user)

    if request.method == 'POST':
        form = ChangeEmailForm(user,
                               request.POST,
                               request.FILES)

        if form.is_valid():
            new_email = form.cleaned_data['email']
            # Change the e-mail address
            user.account.change_email(new_email)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_email_complete',
                                        kwargs={'username': user.username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['user'] = user
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

def detail(request, username, template_name='userena/detail.html', extra_context=None):
    """
    Detailed view of an account.

    **Arguments**

    ``username``
        The username of the user which accounts should be viewed.

    **Keyword arguments**

    ``template_name``
        Name of the template that should be used to display the account.

    ``extra_context``
        Dictionary of variables which should be supplied to the template. The
        ``account`` key is always the current account.

    **Context**

    ``account``
        The currently viewed account.

    """
    account = get_object_or_404(Account,
                                user__username__iexact=username)

    if not extra_context: extra_context = dict()
    extra_context['account'] = account
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

def edit(request, username, edit_form=AccountEditForm,
         template_name='userena/edit_form.html', success_url=None,
         extra_context=None):
    """
    Edit an account. Get's called by ``userena_edit`` url.

    **Arguments**

    ``username``
        The username of the user which account should be edited.

    **Keyword arguments**

    ``edit_form``
        The form that is used to edit the account. The ``save`` method of this
        form will be called when the form ``is_valid``. Defaults to
        ``AccountEditForm`` from userena.

    ``template_name``
        Name of the template that is used to render the ``edit_form``. Defaults
        to ``userena/edit_form.html``.

    ``success_url``
        This value will be passed on to a django ``reverse`` function after the
        form is successfully saved.

    ``extra_context``
        Extra variables that are passed on to the ``template_name`` template.
        ``form`` key will always be the form used to edit the account, and the
        ``account`` key is always the edited account.

    **Context**

    ``form``
        The form that is used to alter the account.

    ``account``
        The account that is edited.

    """
    account = get_object_or_404(Account,
                                user__username__iexact=username)
    form = edit_form(instance=account)

    if request.method == 'POST':
        form = edit_form(request.POST, request.FILES, instance=account)

        if form.is_valid():
            account = form.save()

            messages.success(request, _('Your account has been updated.'),
                             fail_silently=True)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_detail', kwargs={'username': username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['account'] = account
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

def list(request, template_name='userena/list.html'):
    """ Returns a list of all the users """
    return direct_to_template(request,
                              template_name)
