from django.core.validators import email_re
from django.contrib.auth.backends import ModelBackend

from userena.models import UserenaUser

class UserenaAuthenticationBackend(ModelBackend):
    """
    We use a custom backend because the user must be able to supply a ``email``
    or ``username`` to the login form. We will find out ourself what they
    supplied.

    Returns the extended user model ``UserenaUser``.

    """
    def authenticate(self, identification, password=None):
        if email_re.search(identification):
            try: user = UserenaUser.objects.get(email=identification)
            except UserenaUser.DoesNotExist: return None
        else:
            try: user = UserenaUser.objects.get(username=identification)
            except UserenaUser.DoesNotExist: return None
        return user if user.check_password(password) else None

    def get_user(self, user_id):
        try:
            return UserenaUser.objects.get(pk=user_id)
        except UserenaUser.DoesNotExist:
            return None
