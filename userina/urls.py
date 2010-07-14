from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

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
                           {'template': 'userina/verification_complete.html'},
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

                       # Reset password
                       url(r'^password/reset/$',
                           auth_views.password_reset,
                           {'template_name': 'userina/password_reset_form.html',
                            'email_template_name': 'userina/password_reset_message.txt'},
                           name='userina_password_reset'),
                       url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
                           {'template_name': 'userina/password_reset_done.html'},
                           name='userina_password_reset_done'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           {'template_name': 'userina/password_reset_confirm_form.html'},
                           name='userina_password_reset_confirm'),
                       url(r'^password/reset/confirm/complete/$',
                           auth_views.password_reset_complete,
                           {'template_name': 'userina/password_reset_complete.html'}),

                       # Account settings
                       url(r'^me/password/$',
                           auth_views.password_change,
                           {'template_name': 'userina/me_password_form.html'},
                           name='userina_password_change'),
                       url(r'^me/password/complete/$',
                           auth_views.password_change_done,
                           {'template_name': 'userina/me_password_complete.html'},
                           name='userina_password_change_complete'),
                       url(r'^me/email/$',
                           userina_views.email_change,
                           name='userina_email_change'),
                       url(r'^me/email/complete/$',
                           direct_to_template,
                           {'template': 'userina/me_email_complete.html'},
                           name='userina_email_complete'),
                       url(r'^me/$',
                           userina_views.me,
                           name='userina_me'),
                       url(r'^(?P<username>[\w+])/$',
                           userina_views.detail,
                           name='userina_detail'),
 )
