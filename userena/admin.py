from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from guardian.admin import GuardedModelAdmin

from userena.models import UserenaSignup
from userena.utils import get_profile_model
from userena import settings as userena_settings

def accept_signup(modeladmin, request, queryset):
    for obj in queryset:
        key = obj.userena_signup.activation_key
        
        # only if its not already activated
        if key == userena_settings.USERENA_ACTIVATED:
            continue
        obj.userena_signup.activation_key = userena_settings.USERENA_ACTIVATED
        obj.userena_signup.send_approval_email()
        obj.is_active = True
        obj.userena_signup.save()
        obj.save()
        
accept_signup.short_description = _("Accept/Enable a users signup.")

def reject_signup(modeladmin, request, queryset):
    for obj in queryset:
        key = obj.userena_signup.activation_key
        
        # only if its not already rejected
        if key == userena_settings.USERENA_ACTIVATION_REJECTED:
            continue
        obj.userena_signup.activation_key = userena_settings.USERENA_ACTIVATION_REJECTED
        obj.userena_signup.send_rejection_email()
        obj.is_active = False
        obj.userena_signup.save()
        obj.save()
            
reject_signup.short_description = _("Reject/Disable a users signup.")

class UserenaSignupInline(admin.StackedInline):
    model = UserenaSignup
    max_num = 1

class UserenaAdmin(UserAdmin, GuardedModelAdmin):
    inlines = [UserenaSignupInline, ]
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'date_joined')
    actions = [accept_signup, reject_signup]
    
admin.site.unregister(User)
admin.site.register(User, UserenaAdmin)
admin.site.register(get_profile_model())
