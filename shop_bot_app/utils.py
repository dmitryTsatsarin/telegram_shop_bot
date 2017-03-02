# -*- coding: utf-8 -*-
__author__ = 'forward'
from telebot import TeleBot
from django.conf import settings

class ShopTeleBot(TeleBot, object):
    def __init__(self, token, threaded=False, skip_pending=False):
        # треды выключил по умолчанию
        super(ShopTeleBot, self).__init__(token, threaded=threaded, skip_pending=skip_pending)

    def send_photo(self, *args, **kwargs):
        result = super(ShopTeleBot, self).send_photo(*args, **kwargs)
        print 'Send photo is finished'
        return result


def create_shop_telebot(token):
    print 'Get bot function run'
    bot = ShopTeleBot(token)
    return bot

