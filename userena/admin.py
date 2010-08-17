from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from userena.models import UserenaUser, Profile

# TODO: Unregister the current User admin. We can do better.
# admin.site.unregister(User)

admin.site.register(UserenaUser)
admin.site.register(Profile)
