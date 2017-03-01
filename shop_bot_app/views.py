# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
import telebot

from django.http import HttpResponseForbidden
from shop_bot_app.logic import bot # обязательный импорт из logic, после того как привязались все handle функции


def webhooks(request, token):
    print 'Started %s ' % request.get_full_path()

    if 'CONTENT_LENGTH' in request.META and \
                    'CONTENT_TYPE' in request.META and \
                    request.META['CONTENT_TYPE'] == 'application/json':
        #length = int(request.META['CONTENT_LENGTH'])
        json_string = request.body.decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        # Эта функция обеспечивает проверку входящего сообщения
        print 'data=%s' % json_string
        bot.process_new_updates([update])
        print 'finished %s ' % request.get_full_path()
        return HttpResponse('')
    else:
        print 'Forbiden for %s' % request.body
        return HttpResponseForbidden()

