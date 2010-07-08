from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views

from userina import views as userina_views

urlpatterns = patterns('',
                       # Inactive user
                       url(r'^disabled/$',
                           direct_to_template,
                           {'template': 'userina/disabled.html'},
                           name='userina_disabled'),

                       # Activate
                       url(r'^verify/complete/$',
                           direct_to_template,
                           {'template': 'userina/activation_complete.html'},
                           name='userina_verification_complete'),
                       url(r'^verify/(?P<verification_key>\w+)/$',
                           userina_views.verify,
                           name='userina_verify'),

                       # Signin, signout and signup
                       url(r'^signin/$',
                           userina_views.signin,
                           name='userina_signin'),
                       url(r'^signout/$',
                           auth_views.logout,
                           {'template_name': 'userina/signout.html'},
                           name='userina_signout'),
                       url(r'^signup/$',
                           userina_views.signup,
                           name='userina_signup'),
                       url(r'^signup/complete/$',
                           direct_to_template,
                           {'template': 'userina/signup_complete.html'},
                           name='userina_signup_complete'),

                       # Forgot password
                       url(r'^password/reset/$',
                           userina_views.password_reset,
                           name='userina_password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           userina_views.password_reset_confirm,
                           name='userina_password_reset_confirm'),
                       url(r'^password/reset/complete/$',
                           direct_to_template,
                           {'template': 'userina/password_reset_complete.html'}),

                       # Account settings
                       url(r'^password/$',
                           userina_views.password_change,
                           name='userina_password_change'),
                       url(r'^password/complete/$',
                           direct_to_template,
                           {'template': 'userina_password_complete.html'},
                           name='userina_password_complete'),
                       url(r'^profile/$',
                           userina_views.detail,
                           name='userina_detail'),
)
