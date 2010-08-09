from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import Http404
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from userena.forms import (SignupForm, AuthenticationForm, ChangeEmailForm,
                           AccountEditForm)
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

    The key is a SHA1 string. When the SHA1 is found with an ``Account``, the
    ``User`` of that account will be activated. After a successfull activation
    the view will redirect to ``success_url``.  If the SHA1 is not found, the
    user will be shown the ``template_name`` template displaying a fail
    message.

    **Arguments**

    ``activation_key``
        String of a SHA1 string of 40 characters long. A SHA1 is always 160bit
        long, with 4 bits per character this makes it --160/4-- 40 characters
        long.

    **Keyword arguments**

    ``template_name``
        String containing the template name that is used when the
        ``activation_key`` is invalid and the activation failes. Defaults to
        ``userena/activation_fail.html``.

    ``success_url``
        Named URL where the user should be redirected to after a succesfull
        activation. If not specified, will direct to
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

    Verifies a new email address by running ``Account.objects.verify_email``
    method. If the method returns an ``Account`` the user will have his new
    e-mail address set and redirected to ``success_url``. If no ``Account`` is
    returned the user will be represented with a fail message from
    ``template_name``.

    **Arguments**

    ``verification_key``
        String with a SHA1 representing the verification key used to verify a
        new email address.

    **Keyword arguments**

    ``template_name``
        String containing the template name which should be rendered when
        verification fails. When verification is succesfull, no template is
        needed because the user will be redirected to ``success_url``.

    ``success_url``
        Named URL which is redirected to after a succesfull verification.
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
    Signin using your email or username and password.

    Signs a user in by combining email/username with password. If the
    combination is correct and the user ``is_active`` the
    ``redirect_signin_function`` is called with the arguments
    ``REDIRECT_FIELD_NAME`` and an instance of the ``User`` whois is trying the
    login. The returned value of the function will be the URL that is
    redirected to.

    A user can also select to be remembered for ``USERENA_REMEMBER_DAYS``.

    **Keyword arguments**

    ``auth_form``
        Form to use for signing the user in. Defaults to the
        ``AuthenticationForm`` supplied by userena.

    ``template_name``
        String defining the name of the template to use. Defaults to
        ``userena/signin_form.html``.

    ``redirect_field_name``
        Form field name which contains the value for a redirect to the
        successing page. Defaults to ``next`` and is set in
        ``REDIRECT_FIELD_NAME`` setting.

    ``redirect_signin_function``
        Function which handles the redirect. This functions gets the value of
        ``REDIRECT_FIELD_NAME`` and the ``User`` who has logged in. It must
        return a string which specifies the URI to redirect to.

    ``extra_context``
        A dictionary containing extra variables that should be passed to the
        rendered template. The ``form`` key is always the ``auth_form``.

    **Context**

    ``form``
        Form used for authentication supplied by ``auth_form``.

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
        Form that will be used to sign a user. Defaults to userena's
        ``forms.SignupForm``.

    ``template_name``
        String containing the template name that will be used to display the
        signup form. Defaults to ``userena/signup_form.html``.

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
        Form supplied by ``signup_form``.

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
    Change email address

    **Arguments**

    ``username``
        String of the username which specifies the current account.

    **Keyword arguments**

    ``form``
        Form that will be used to change the email address. Defaults to
        ``ChangeEmailForm`` supplied by userena.

    ``template_name``
        String containing the template to be used to display the email form.
        Defaults to ``userena/email_form.html``.

    ``success_url``
        Named URL where the user will get redirected to when succesfully
        changing their email address.  When not suplied will redirect to
        ``userena_email_complete`` URL.

    ``extra_context``
        Dictionary containing extra variables that can be used to render the
        template. The ``form`` key is always the form supplied by the keyword
        argument ``form`` and the ``user`` key by the user whose email address
        is being changed.

    **Context**

    ``form``
        Form that is used to change the email address supplied by ``form``.

    ``user``
        Instance of the ``User`` whose email address is about to be changed.

    **Todo**

    Need to have per-object permissions, which enables users with the correct
    permissions to alter the email address of others.

    """
    user = get_object_or_404(User, username__iexact=username)
    form = ChangeEmailForm(user)

    if request.method == 'POST':
        form = ChangeEmailForm(user,
                               request.POST,
                               request.FILES)

        if form.is_valid():
            new_email = form.cleaned_data['email']
            # Change the email address
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
        String of the username of which the account should be viewed.

    **Keyword arguments**

    ``template_name``
        String representing the template name that should be used to display
        the account.

    ``extra_context``
        Dictionary of variables which should be supplied to the template. The
        ``account`` key is always the current account.

    **Context**

    ``account``
        Instance of the currently edited ``Account``.

    """
    account = get_object_or_404(Account,
                                user__username__iexact=username)

    if not extra_context: extra_context = dict()
    extra_context['account'] = account
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

@secure_required
@login_required
def edit(request, username, edit_form=AccountEditForm,
         template_name='userena/edit_form.html', success_url=None,
         extra_context=None):
    """
    Edit an account.

    Edits an account selected by the supplied username. If the account is
    succesfully edited will redirect to ``success_url``.

    **Arguments**

    ``username``
        Username of the user which account should be edited.

    **Keyword arguments**

    ``edit_form``
        Form that is used to edit the account. The ``save`` method of this form
        will be called when the form ``is_valid``. Defaults to
        ``AccountEditForm`` from userena.

    ``template_name``
        String of the template that is used to render the ``edit_form``.
        Defaults to ``userena/edit_form.html``.

    ``success_url``
        Named URL which be passed on to a django ``reverse`` function after the
        form is successfully saved. Defaults to the ``userena_detail`` url.

    ``extra_context``
        Dictionary containing variables that are passed on to the
        ``template_name`` template.  ``form`` key will always be the form used
        to edit the account, and the ``account`` key is always the edited
        account.

    **Context**

    ``form``
        Form that is used to alter the account.

    ``account``
        Instance of the ``Account`` that is edited.

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

@secure_required
@login_required
def password_change(request, username, template_name='userena/password_form.html',
                    pass_form=PasswordChangeForm, success_url=None, extra_context=None):
    """ Change password of user.

    This view is almost a mirror of the view supplied in
    ``contrib.auth.views.password_change``, with the minor change that in this
    view we also use the username to change the password. This was needed to
    keep our URLs logical (and REST) accross the entire application. And that
    in a later stadium administrators can also change the users password
    through the web application itself.

    **Arguments**

    ``username``

        String supplying the username of the user who's password is about to be
        changed.

    **Keyword arguments**

    ``template_name``
        String of the name of the template that is used to display the password
        change form. Defaults to ``userena/password_form.html``.

    ``pass_form``
        Form used to change password. Default is the form supplied by Django
        itself named ``PasswordChangeForm``.

    ``success_url``
        Named URL that is passed onto a ``reverse`` function with ``username``
        of the active user. Defaults to the ``userena_password_complete`` URL.

    ``extra_context``
        Dictionary of extra variables that are passed on the the template. The
        ``form`` key is always used by the form supplied by ``pass_form``.

    **Context**

    ``form``
        Form used to change the password.

    ``account``
        The current active account.

    """
    account = get_object_or_404(Account,
                                user__username__iexact=username)

    form = pass_form(user=account.user)

    if request.method == "POST":
        form = pass_form(user=account.user, data=request.POST)
        if form.is_valid():
            form.save()

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_password_change_complete',
                                        kwargs={'username': account.user.username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['account'] = account
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

def list(request, page=1, template_name='userena/list.html', paginate_by=50,
         extra_context=None):
    """
    Returns a list of all accounts that are public.

    **Keyword arguments**

    ``page``
        Integer of the active page used for pagination. Defaults to the first
        page.

    ``template_name``
        String defining the name of the template that is used to render the
        list of all users. Defaults to ``userena/list.html``.

    ``paginate_by``
        Integer defining the amount of displayed accounts per page. Defaults to
        50 accounts per page.

    ``extra_context``
        Dictionary of variables that are passed on to the ``template_name``
        template.

    **Context**

    ``account_list``
        A list of accounts.

    ``is_paginated``
        A boolean representing whether the results are paginated.

    If the result is paginated. It will also contain the following variables:

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """
    try:
        page = int(request.GET.get('page', None))
    except TypeError, ValueError:
        page = page

    if not extra_context: extra_context = dict()
    return list_detail.object_list(request,
                                   queryset=Account.objects.all(),
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name='account')
