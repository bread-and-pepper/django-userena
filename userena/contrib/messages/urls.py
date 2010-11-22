from django.conf.urls.defaults import *

from userena.contrib.messages import views as messages_views

urlpatterns = patterns('',
    url(r'^$',
        messages_views.list,
        name='userena_messages_list')
)
