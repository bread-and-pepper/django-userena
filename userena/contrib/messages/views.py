from django.contrib.auth.decorators import login_required

@login_required
def message_list(request, page=1, paginate_by=50, mailbox='inbox',
                 template_name='message_list.html'):
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
        following three strings:

        =========== ===========================================
        inbox       the incoming messages
        outbox      the sent messsages
        drafts      composed but not sent messages
        thrash      messages that are marked as deleted
        =========== ===========================================

    :param template_name:
        String defining the name of the template that is used to render the
        list of messages. Defaults to ``list.html``.

    **Context**

    ``message_list``
        A list of messages.

    ``is_paginated``
        A boolean representing whether the results are paginated.

    If the result is paginated, the context will also contain the following variables:

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """
    try:
        page = int(request.GET.get('page', None))
    except TypeError, ValueError:
        page = page

def message_detail(request):
    pass

def message_compose(request):
    pass

def message_remove(request):
    pass

def message_unremove(request):
    pass
