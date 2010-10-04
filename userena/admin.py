from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from userena.models import UserenaSignup
from userena.utils import get_profile_model

class UserenaSignupInline(admin.TabularInline):
    model = UserenaSignup
    max_num = 1

class UserenaAdmin(UserAdmin):
    inlines = [UserenaSignupInline, ]

admin.site.unregister(User)
admin.site.register(User, UserenaAdmin)
admin.site.register(get_profile_model())
