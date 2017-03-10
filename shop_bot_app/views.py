# -*- coding: utf-8 -*-
import logging

import sys
import traceback
import telebot as telebot_lib
from django.http import HttpResponse
from django.http import HttpResponseForbidden

from shop_bot_app.bot_routing import initialize_bot_with_routing2
from shop_bot_app.helpers import get_request_data
from shop_bot_app.models import Bot

logger = logging.getLogger(__name__)


def webhooks(request, token):
    try:
        print 'Started %s ' % request.get_full_path()

        if 'CONTENT_LENGTH' in request.META and 'CONTENT_TYPE' in request.META and request.META['CONTENT_TYPE'] == 'application/json':
            json_string = get_request_data(request)
            update = telebot_lib.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            logger.info(u'data=%s' % json_string.decode('unicode-escape'))

            if Bot.objects.filter(telegram_token=token).exists():
                shop_telebot = initialize_bot_with_routing2(token)
                shop_telebot.process_new_updates([update])
            else:
                logger.error('Token "%s" is not found' % token)
            return HttpResponse('')
        else:
            print 'Forbiden for %s' % request.body
            return HttpResponseForbidden()
    except Exception as e:
        t, v, tb = sys.exc_info()
        traceback.print_exc(tb, file=sys.stdout)
        raise

