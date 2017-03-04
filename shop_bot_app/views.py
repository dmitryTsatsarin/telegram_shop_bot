# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
import telebot as telebot_lib

from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from shop_bot_app.logic import initialize_bot_with_routing
from shop_bot_app.models import Bot

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def webhooks(request, token):
    print 'Started %s ' % request.get_full_path()

    if 'CONTENT_LENGTH' in request.META and \
                    'CONTENT_TYPE' in request.META and \
                    request.META['CONTENT_TYPE'] == 'application/json':
        json_string = request.body.decode("utf-8")
        update = telebot_lib.types.Update.de_json(json_string)
        # Эта функция обеспечивает проверку входящего сообщения
        logger.info(u'data=%s' % json_string.decode('unicode-escape'))

        if Bot.objects.filter(telegram_token=token).exists():
            shop_telebot = initialize_bot_with_routing(token, request.session)
            shop_telebot.process_new_updates([update])
        else:
            logger.error('Token "%s" is not found')
        return HttpResponse('')
    else:
        print 'Forbiden for %s' % request.body
        return HttpResponseForbidden()

