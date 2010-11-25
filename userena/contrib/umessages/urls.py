from django.conf.urls.defaults import *
from django.shortcuts import redirect

from userena.contrib.umessages import views as messages_views

urlpatterns = patterns('',
    url(r'^$',
        redirect,
        {'url': 'inbox/'}),

    url(r'^inbox/$',
        messages_views.message_list,
        {'mailbox': 'inbox'},
        name='userena_umessages_inbox'),

    url(r'^outbox/$',
        messages_views.message_list,
        {'mailbox': 'outbox'},
        name='userena_umessages_outbox'),

    url(r'^drafts/$',
        messages_views.message_list,
        {'mailbox': 'drafts'},
        name='userena_umessages_drafts'),

    url(r'^trash/$',
        messages_views.message_list,
        {'mailbox': 'trash'},
        name='userena_umessages_trash'),

    url(r'^compose/$',
        messages_views.message_compose,
        name='userena_umessages_compose'),

    url(r'^compose/(?P<recipients>[\+\w]+)/$',
        messages_views.message_compose,
        name='userena_umessages_compose_to'),

    url(r'^reply/(?P<parent_id>[\d]+)/$',
        messages_views.message_compose,
        name='userena_umessages_reply'),

    url(r'^view/(?P<message_id>[\d]+)/$',
        messages_views.message_detail,
        name='userena_umessages_detail'),

    url(r'^remove/$',
        messages_views.message_remove,
        name='userena_umessages_remove'),

    url(r'^unremove/$',
        messages_views.message_unremove,
        name='userena_umessages_unremove'),
)
