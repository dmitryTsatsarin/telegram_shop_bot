# -*- coding: utf-8 -*-
__author__ = 'forward'
from .common import *

import os
import raven

RAVEN_CONFIG = {
    'dsn': 'https://87ee6b086aa2451ba3af12e24b3020ea:6b5d14816e8a401585c8a399c6dcf4e3@sentry.io/140482',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'shop_bot',
        'USER': 'webrunner',
        'PASSWORD': 'ZHkv8GD4Zab2g4HHNqPn',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(message)s'
        },
    },
    'handlers': {
        'sentry_self_test_handler': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['sentry_self_test_handler'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'celery': {
            'level': 'INFO',
            'handlers': ['sentry','console'],
            'propagate': False,
        },
        'shop_bot_app': {
            'level': 'INFO',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        }
    },
}
CSRF_COOKIE_SECURE = False # выставить в True, когда будет https (https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/)
ALLOWED_HOSTS = ['*', '46.101.235.119']

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'amqp://rabbitusername:6cae046bd8de29@localhost:5672//telegram_shop_bot'

WEBHOOK_HOST = 'bots.artbelka.by'
WEBHOOK_LISTEN = 'bots.artbelka.by'
WEBHOOK_PORT = 443
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
#WEBHOOK_SSL_CERT = '/etc/letsencrypt/live/bots.artbelka.miramik.ru/fullchain.pem'
#WEBHOOK_SSL_PRIV = '/etc/letsencrypt/live/bots.artbelka.miramik.ru/privkey.pem'
