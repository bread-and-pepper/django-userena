from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from userenity.models import Account

admin.site.unregister(User)
class AccountInline(admin.StackedInline):
    model = Account

class AccountAdmin(UserAdmin):
    inlines = [AccountInline]

admin.site.register(User, AccountAdmin)
