from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.models import User
from django.template import loader
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.contrib.auth import REDIRECT_FIELD_NAME

from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact
from userena.contrib.umessages.forms import ComposeForm
from userena import settings as userena_settings

import datetime

@login_required
def message_list(request, page=1, paginate_by=50,
                 template_name="umessages/message_list.html",
                 extra_context=None, **kwargs):
    """

    Returns the message list for this user. This is a list contacts
    which at the top has the user that the last conversation was with. This is
    an imitation of the iPhone SMS functionality.

    :param page:
        Integer of the active page used for pagination. Defaults to the first
        page.

    :param paginate_by:
        Integer defining the amount of displayed messages per page.
        Defaults to 50 messages per per page.

    :param template_name:
        String of the template that is rendered to display this view.

    :param extra_context:
        Dictionary of variables that will be made available to the template.

    If the result is paginated, the context will also contain the following
    variables.

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """
    queryset = MessageContact.objects.get_contacts_for(request.user)

    if not extra_context: extra_context = dict()
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name="message",
                                   **kwargs)

@login_required
def message_detail(request, username, page=1, paginate_by=10,
                   template_name="umessages/message_detail.html",
                   extra_context=None, **kwargs):
    """
    Returns a conversation between two users

    :param username:
        String containing the username of :class:`User` of whom the
        conversation is with.

    :param page:
        Integer of the active page used for pagination. Defaults to the first
        page.

    :param paginate_by:
        Integer defining the amount of displayed messages per page.
        Defaults to 50 messages per per page.

    :param extra_context:
        Dictionary of variables that will be made available to the template.

    :param template_name:
        String of the template that is rendered to display this view.

    If the result is paginated, the context will also contain the following
    variables.

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """
    recipient = get_object_or_404(User,
                                  username__iexact=username)
    queryset = Message.objects.get_conversation_between(request.user,
                                                        recipient)

    # Update all the messages that are unread.
    message_pks = [m.pk for m in queryset]
    unread_list = MessageRecipient.objects.filter(message__in=message_pks,
                                                  user=request.user,
                                                  read_at__isnull=True)
    now = datetime.datetime.now()
    unread_list.update(read_at=now)

    if not extra_context: extra_context = dict()
    extra_context['recipient'] = recipient
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name="message",
                                   **kwargs)

@login_required
def message_compose(request, recipients=None, compose_form=ComposeForm,
                    success_url=None, template_name="umessages/message_form.html",
                    recipient_filter=None, extra_context=None):
    """
    Compose a new message

    :recipients:
        String containing the usernames to whom the message is send to. Can be
        multiple username by seperating them with a ``+`` sign.

    :param compose_form:
        The form that is used for getting neccesary information. Defaults to
        :class:`ComposeForm`.

    :param success_url:
        String containing the named url which to redirect to after successfull
        sending a message. Defaults to ``userena_umessages_list`` if there are
        multiple recipients. If there is only one recipient, will redirect to
        ``userena_umessages_detail`` page, showing the conversation.

    :param template_name:
        String containing the name of the template that is used.

    :param recipient_filter:
        A list of :class:`User` that don"t want to receive any messages.

    :param extra_context:
        Dictionary with extra variables supplied to the template.

    **Context**

    ``form``
        The form that is used.

    """
    initial_data = dict()

    if recipients:
        username_list = [r.strip() for r in recipients.split("+")]
        recipients = [u for u in User.objects.filter(username__in=username_list)]
        initial_data["to"] = recipients

    form = compose_form(initial=initial_data)
    if request.method == "POST":
        form = compose_form(request.POST)
        if form.is_valid():
            requested_redirect = request.REQUEST.get("next", False)

            message = form.save(request.user)
            recipients = form.cleaned_data['to']

            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, _('Message is sent.'),
                                 fail_silently=True)

            requested_redirect = request.REQUEST.get(REDIRECT_FIELD_NAME,
                                                     False)

            # Redirect mechanism
            redirect_to = reverse('userena_umessages_list')
            if requested_redirect: redirect_to = requested_redirect
            elif success_url: redirect_to = success_url
            elif len(recipients) == 1:
                redirect_to = reverse('userena_umessages_detail',
                                      kwargs={'username': recipients[0].username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context["form"] = form
    extra_context["recipients"] = recipients
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

@login_required
@require_http_methods(["POST"])
def message_remove(request, undo=False):
    """
    A ``POST`` to remove messages.

    :param undo:
        A Boolean that if ``True`` unremoves messages.

    POST can have the following keys:

        ``message_pks``
            List of message id's that should be deleted.

        ``next``
            String containing the URI which to redirect to after the keys are
            removed. Redirect defaults to the inbox view.

    The ``next`` value can also be supplied in the URI with ``?next=<value>``.

    """
    message_pks = request.POST.getlist('message_pks')
    redirect_to = request.REQUEST.get('next', False)

    if message_pks:
        # Check that all values are integers.
        valid_message_pk_list = set()
        for pk in message_pks:
            try: valid_pk = int(pk)
            except (TypeError, ValueError): pass
            else:
                valid_message_pk_list.add(valid_pk)

        # Delete all the messages, if they belong to the user.
        now = datetime.datetime.now()
        changed_message_list = set()
        for pk in valid_message_pk_list:
            message = get_object_or_404(Message, pk=pk)

            # Check if the user is the owner
            if message.sender == request.user:
                if undo:
                    message.sender_deleted_at = None
                else:
                    message.sender_deleted_at = now
                message.save()
                changed_message_list.add(message.pk)

            # Check if the user is a recipient of the message
            if request.user in message.recipients.all():
                mr = message.messagerecipient_set.get(user=request.user,
                                                      message=message)
                if undo:
                    mr.deleted_at = None
                else:
                    mr.deleted_at = now
                mr.save()
                changed_message_list.add(message.pk)

        # Send messages
        if (len(changed_message_list) > 0) and userena_settings.USERENA_USE_MESSAGES:
            if undo:
                message = ungettext('Message is succesfully restored.',
                                    'Messages are succesfully restored.',
                                    len(changed_message_list))
            else:
                message = ungettext('Message is successfully removed.',
                                    'Messages are successfully removed.',
                                    len(changed_message_list))

            messages.success(request, message, fail_silently=True)

    if redirect_to: return redirect(redirect_to)
    else: return redirect(reverse('userena_umessages_list'))
