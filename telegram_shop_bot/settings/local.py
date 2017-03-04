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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', 'console'],
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
            'handlers': ['console'],
            'propagate': False,
        },
        'telebot': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'INFO',
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
            'handlers': ['console','sentry'],
            'propagate': False,
        },
        'shop_bot_app': {
            'level': 'INFO',
            'handlers': ['console', 'sentry'],
            'propagate': False,
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.prod.sqlite3'),
    },
    'stat': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.stat.sqlite3'),
    }
}

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'amqp://myusername:mypassword@localhost:5672//telegram_shop_bot'

ALLOWED_HOSTS = ['*', '2e6f2ab8.ngrok.io']


WEBHOOK_HOST = 'a0c4305f.ngrok.io'
WEBHOOK_LISTEN = 'a0c4305f.ngrok.io'
WEBHOOK_PORT = 443

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/mails'

LOGUTILS_REQUEST_TIME_THRESHOLD = 20 # уведомлять о всех запросах дольше 10 секунд