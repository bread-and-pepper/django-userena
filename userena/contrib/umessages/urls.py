from django.conf.urls import *
from userena.contrib.umessages import views as messages_views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^compose/$',
        messages_views.message_compose,
        name='userena_umessages_compose'),

    url(r'^compose/(?P<recipients>[\+\.\w]+)/$',
        messages_views.message_compose,
        name='userena_umessages_compose_to'),

    url(r'^reply/(?P<parent_id>[\d]+)/$',
        messages_views.message_compose,
        name='userena_umessages_reply'),

    url(r'^view/(?P<username>[\.\w]+)/$',
        login_required(messages_views.MessageDetailListView.as_view()),
        name='userena_umessages_detail'),

    url(r'^remove/$',
        messages_views.message_remove,
        name='userena_umessages_remove'),

    url(r'^unremove/$',
        messages_views.message_remove,
        {'undo': True},
        name='userena_umessages_unremove'),

    url(r'^$',
        login_required(messages_views.MessageListView.as_view()),
        name='userena_umessages_list'),
)
