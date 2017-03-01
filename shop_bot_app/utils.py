# -*- coding: utf-8 -*-
__author__ = 'forward'
import telebot
from django.conf import settings

def get_bot():
    print 'Get bot function run'
    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
    return bot

bot = get_bot()
