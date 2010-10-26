from django.core.validators import email_re
from django.contrib.auth.backends import ModelBackend

from django.contrib.auth.models import User

class UserenaAuthenticationBackend(ModelBackend):
    """
    We use a custom backend because the user must be able to supply a ``email``
    or ``username`` to the login form. We will find out ourself what they
    supplied.

    Returns the user `User`.

    **Arguments**

    ``identification``
        A string containing the username or e-mail of the user that is trying
        to authenticate.

    **Keyword arguments**

    ``password``
        Optional string containing the password for the user.

    ``check_password``
        Boolean that defines if the password should be checked for this user.
        Always keep this ``True``. This is used at activation when a user opens
        a page with a secret hash.

    """
    def authenticate(self, identification, password=None, check_password=True):
        if email_re.search(identification):
            try: user = User.objects.get(email__iexact=identification)
            except User.DoesNotExist: return None
        else:
            try: user = User.objects.get(username__iexact=identification)
            except User.DoesNotExist: return None
        if check_password:
            if user.check_password(password):
                return user
            return None
        else: return user

    def get_user(self, user_id):
        try: return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
