import django

if django.VERSION < (1, 6):
    from .test_backends import *
    from .test_commands import *
    from .test_privacy import *
    from .tests_decorators import *
    from .tests_forms import *
    from .tests_managers import *
    from .tests_middleware import *
    from .tests_models import *
    from .tests_utils import *
    from .tests_views import *