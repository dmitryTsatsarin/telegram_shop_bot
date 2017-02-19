# -*- coding: utf-8 -*-
__author__ = 'forward'

from .common import *

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'amqp://myusername:mypassword@localhost:5672//telegram_shop_bot'