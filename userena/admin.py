from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _
from guardian.admin import GuardedModelAdmin

from userena.models import UserenaSignup
from userena.utils import get_profile_model, get_user_model

class UserenaSignupInline(admin.StackedInline):
    model = UserenaSignup
    max_num = 1

class UserenaAdmin(UserAdmin, GuardedModelAdmin):
    inlines = [UserenaSignupInline, ]
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserenaAdmin)
admin.site.register(get_profile_model())
