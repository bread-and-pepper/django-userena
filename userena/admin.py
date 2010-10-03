from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from userena.models import UserenaProfile
from userena.utils import get_profile_model

# TODO: Unregister the current User admin. We can do better.
# admin.site.unregister(User)

admin.site.register(UserenaProfile)
admin.site.register(get_profile_model())
