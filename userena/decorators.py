from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils.decorators import available_attrs

from userena import settings as userena_settings

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

def secure_required(view_func):
    """
    Decorator to switch an url from http to https.

    If a view is accessed through http and this decorator is applied to that
    view, than it will return a permanent redirect to the secure (https)
    version of the same view.

    The decorator also must check that ``USERENA_USE_HTTPS`` is enabled. If
    disabled, it should not redirect to https because the project doesn't
    support it.

    """
    def _wrapped_view(request, *args, **kwargs):
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            request.is_secure = lambda: request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        if 'HTTP_X_FORWARDED_PROTOCOL' in request.META:
            request.is_secure = lambda: request.META['HTTP_X_FORWARDED_PROTOCOL'] == 'https'

        if not request.is_secure():
            if userena_settings.USERENA_USE_HTTPS:
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponsePermanentRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
