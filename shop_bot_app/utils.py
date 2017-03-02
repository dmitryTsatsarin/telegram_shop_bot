# -*- coding: utf-8 -*-
__author__ = 'forward'
from telebot import TeleBot
from django.conf import settings

class ShopTeleBot(TeleBot):
    pass

def create_shop_telebot(token):
    print 'Get bot function run'
    bot = ShopTeleBot(token)
    return bot

