from settings import *

import json

DEBUG = False
TEMPLATE_DEBUG = DEBUG
with open('/home/dotcloud/environment.json') as f:
    env = json.load(f)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'django_userena',
            'USER': env['DOTCLOUD_DB_SQL_LOGIN'],
            'PASSWORD': env['DOTCLOUD_DB_SQL_PASSWORD'],
            'HOST': env['DOTCLOUD_DB_SQL_HOST'],
            'PORT': int(env['DOTCLOUD_DB_SQL_PORT']),
        }
    }

    # Email settings
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = env['GMAIL_USER']
    EMAIL_HOST_PASSWORD = env['GMAIL_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = "Userena <hello@breadandpepper.com>"

# Media and static
MEDIA_ROOT = '/home/dotcloud/data/media/'
STATIC_ROOT = '/home/dotcloud/volatile/static/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': '/var/log/supervisor/userena.log',
            'maxBytes': 1024*1024*25, # 25 MB
            'backupCount': 5,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        # Catch All Logger -- Captures any other logging
        '': {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

