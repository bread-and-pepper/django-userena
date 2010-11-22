from django.conf.urls.defaults import *
from django.shortcuts import redirect

from userena.contrib.messages import views as messages_views

urlpatterns = patterns('',
    url(r'^$',
        redirect,
        {'url': 'inbox/'}),

    url(r'^inbox/$',
        messages_views.inbox,
        name='userena_messages_inbox'),

    url(r'^outbox/$',
        messages_views.outbox,
        name='userena_messages_outbox'),

    url(r'^drafts/$',
        messages_views.drafts,
        name='userena_messages_drafts'),

    url(r'^compose/$',
        messages_views.compose,
        name='userena_messages_compose'),

    url(r'^compose/(?P<recipient>[\+\w]+)/$',
        messages_views.compose,
        name='userena_messages_compose_to'),

    url(r'^reply/(?P<message_id>[\d]+)/$',
        messages_views.reply,
        name='userena_messages_reply'),

    url(r'^view/(?P<message_id>[\d]+)/$',
        messages_views.view,
        name='userena_messages_detail'),

    url(r'^delete/(?P<message_id>[\d]+)/$',
        messages_views.delete,
        name='userena_messages_delete'),

    url(r'^undelete/(?P<message_id>[\d]+)/$',
        messages_views.undelete,
        name='userena_messages_undelete'),

    url(r'^trash/$',
        messages_views.trash,
        name='userena_messages_trash'),
)
