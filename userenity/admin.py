from django.contrib import admin

from userenity.models import Account
from userenity.forms import AccountForm

class AccountAdmin(admin.ModelAdmin):
    form = AccountForm

admin.site.register(Account, AccountAdmin)
