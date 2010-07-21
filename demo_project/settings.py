import os, sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.dirname(SITE_ROOT))

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'demo_project.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

if DEBUG:
    # Use the Python SMTP debugging server. You can run it with:
    # ``python -m smtpd -n -c DebuggingServer localhost:1025``.
    EMAIL_PORT = 1025

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

SECRET_KEY = 'sx405#tc)5m@s#^jh5l7$k#cl3ekg)jtbo2ds(n(kw@gp0t7x@'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'userina.UserinaAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'demo_project.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'easy_thumbnails',
    'userina',
)

# Settings required for userina
LOGIN_REDIRECT_URL = '/accounts/me/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'
