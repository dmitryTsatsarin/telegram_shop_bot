# -*- coding: utf-8 -*-
__author__ = 'forward'

import telebot
from django.conf import settings

def initialize_bot_cert():
    print 'Инициализация начата'
    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
    bot.remove_webhook()

    # Ставим заново вебхук
    # bot.set_webhook(url=settings.WEBHOOK_URL_BASE + settings.WEBHOOK_URL_PATH, certificate=open(settings.WEBHOOK_SSL_CERT, 'r'))
    url = '%s%s' % (settings.WEBHOOK_URL_BASE, settings.WEBHOOK_URL_PATH)
    print 'url=%s' % url
    bot.set_webhook(url=url)
    print 'Инициализация закончена'