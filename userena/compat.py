# -*- coding: utf-8 -*-
from collections import defaultdict
import django


# this default dict will store all compat quirks for parameters of
# django.contrib.auth views
auth_views_compat_quirks = defaultdict(lambda: dict())

# below are quirks we must use because we can't change some userena API's
# like (url names)
if django.VERSION >= (1, 6, 0):  # pragma: no cover
    # in django >= 1.6.0 django.contrib.auth.views.reset no longer looks
    # for django.contrib.auth.views.password_reset_done but for
    # password_reset_done named url. To avoid duplicating urls we
    # provide custom post_reset_redirect
    auth_views_compat_quirks['userena_password_reset'] = {
        'post_reset_redirect': 'userena_password_reset_done',
    }

    # same case as above
    auth_views_compat_quirks['userena_password_reset_confirm'] = {
        'post_reset_redirect': 'userena_password_reset_complete',
    }
if django.VERSION >= (1, 7, 0):
    # Django 1.7 added a new argument to django.contrib.auth.views.password_reset
    # called html_email_template_name which allows us to pass it the html version
    # of the email
    auth_views_compat_quirks['html_email_template_name'] = 'userena/emails/password_reset_message.html'


# below are backward compatibility fixes
password_reset_uid_kwarg = 'uidb64'
if django.VERSION < (1, 6, 0):  # pragma: no cover
    # Django<1.6.0 uses uidb36, we construct urlpattern depending on this
    password_reset_uid_kwarg = 'uidb36'


# SiteProfileNotAvailable compatibility
if django.VERSION < (1, 7, 0):  # pragma: no cover
    from django.contrib.auth.models import SiteProfileNotAvailable
else:  # pragma: no cover
    class SiteProfileNotAvailable(Exception):
        pass


if django.VERSION < (1, 7, 0):
    from django.db.models import get_model
else:
    from django.apps import apps
    get_model = apps.get_model


# optparse/argparse compatibility helper for simple cases (long options only)
# for an example useage see userena/management/commands/check_permissions.py
if django.VERSION < (1, 8):
    from optparse import make_option
    def make_options(options):
        return list(make_option(opt, **attrs) for opt, attrs in options)
else:
    def make_options(options):
        return ()
