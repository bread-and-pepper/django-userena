from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import User, Group

from userena.contrib.umessages.models import Message, MessageRecipient

class MessageRecipientInline(admin.TabularInline):
    """ Inline message recipients """
    model = MessageRecipient

class MessageAdmin(admin.ModelAdmin):
    """ Admin message class with inline recipients """
    inlines = [
        MessageRecipientInline,
    ]

    fieldsets = (
        (None, {
            'fields': (
                'parent_msg', 'sender', 'subject', 'body',
            ),
            'classes': ('monospace' ),
        }),
        (_('Date/time'), {
            'fields': (
                'sent_at',
                'sender_deleted_at',
            ),
            'classes': ('collapse', 'wide'),
        }),
    )
    list_display = ('subject', 'sender', 'sent_at')
    list_filter = ('sent_at', 'sender')
    search_fields = ('subject', 'body')

admin.site.register(Message, MessageAdmin)
