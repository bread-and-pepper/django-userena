from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from userena import settings as userena_settings

def secure_required(view_func):
    """ Decorator makes sure URL is accessed over https. """
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if userena_settings.USERENA_USE_HTTPS:
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponsePermanentRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
