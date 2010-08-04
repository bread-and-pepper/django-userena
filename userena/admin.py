from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from userena.models import Account

# Unregister the current User admin. We can do better.
admin.site.unregister(User)

class AccountInline(admin.StackedInline):
    fieldsets = (
        (None, {
            'fields': ('mugshot', 'gender', 'website', 'location',
                       'birth_date', 'about_me')
        }),
        (_('Account management fields'), {
            'classes': ('collapse',),
            'fields': ('last_active', 'activation_key',
                       'activation_key_created', 'activation_notification_send',
                       'email_new', 'email_verification_key')
        }),
    )
    model = Account

class AccountAdmin(UserAdmin):
    inlines = [AccountInline]

admin.site.register(User, AccountAdmin)
