import django

if django.VERSION < (1, 6):
    from .test_fields import *
    from .test_forms import *
    from .test_managers import *
    from .test_models import *
    from .test_views import *
