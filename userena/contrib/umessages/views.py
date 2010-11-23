from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail
from django.http import Http404

from userena.contrib.umessages.models import Message

@login_required
def message_list(request, page=1, paginate_by=50, mailbox='inbox',
                 template_name='messages/message_list.html', extra_context=None,
                 **kwargs):
    """

    List a folder of specific type for this user.

    :param page:
        Integer of the active page used for pagination. Defaults to the first
        page.

    :param paginate_by:
        Integer defining the amount of displayed messages per page.
        Defaults to 50 messages per per page.

    :param mailbox:
        String defining the mailbox that is currently opened. Can be one of the
        following four strings:

        ``inbox``
            Incoming messages.

        ``outbox``
            Sent messsages.

        ``drafts``
            Composed but not sent messages.

        ``trash``
            Messages that are marked as deleted.

    :param template_name:
        String defining the name of the template that is used to render the
        list of messages. Defaults to ``list.html``.

    :param extra_context:
        A dictionary of variables that are passed on to the template.

    **Context**

    ``message_list``
        A list of messages.

    ``is_paginated``
        A boolean representing whether the results are paginated.

    ``mailbox``
        The current active mailbox.

    If the result is paginated, the context will also contain the following
    variables.

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """
    try:
        page = int(request.GET.get('page', None))
    except TypeError, ValueError:
        page = page

    queryset = Message.objects.get_mailbox_for(user=request.user,
                                               mailbox=mailbox)

    if not extra_context: extra_context = dict()
    extra_context['mailbox'] = mailbox
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name='message',
                                   **kwargs)

@login_required
def message_detail(request):
    pass

@login_required
def message_compose(request):
    pass

@login_required
def message_remove(request):
    pass

@login_required
def message_unremove(request):
    pass
