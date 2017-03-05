# -*- coding: utf-8 -*-
from django.core.mail import send_mail


from shop_bot_app.models import Bot

__author__ = 'forward'

from  shop_bot_app.utils import create_shop_telebot
from django.conf import settings
#
# def initialize_bot_cert():
#     print 'Инициализация начата'
#     bot = TeleBot(settings.TELEGRAM_TOKEN)
#     bot.remove_webhook()
#
#     # Ставим заново вебхук
#     # bot.set_webhook(url=settings.WEBHOOK_URL_BASE + settings.WEBHOOK_URL_PATH, certificate=open(settings.WEBHOOK_SSL_CERT, 'r'))
#     url = '%s%s' % (settings.WEBHOOK_URL_BASE, settings.WEBHOOK_URL_PATH)
#     print 'url=%s' % url
#     bot.set_webhook(url=url)
#     print 'Инициализация закончена'


def initialize_all_webhooks():
    print 'Инициализация начата'
    bots = list(Bot.objects.all())
    for bot in bots:
        shop_telebot = create_shop_telebot(bot.telegram_token)
        shop_telebot.remove_webhook()

        # Ставим заново вебхук
        url = get_webhook_url(bot.telegram_token)
        print 'bot = %s, url=%s' % (bot.name, url)
        shop_telebot.set_webhook(url=url)
    print 'Инициализация закончена'


def initialize_webhook_for_bot(token):
    print 'Инициализация начата'
    shop_telebot = create_shop_telebot(token)
    shop_telebot.remove_webhook()

    # Ставим заново вебхук
    url = get_webhook_url(token)
    print 'url=%s' % url
    shop_telebot.set_webhook(url=url)
    print 'Инициализация закончена'


def get_webhook_url(token):
    return "%s/webhooks/%s/" % (settings.WEBHOOK_URL_BASE, token)


def send_mail_to_the_shop(text):
    shop_administrator_email = settings.EMAIL_BOT_ADMIN # на данный момент пока администратор магазина это админ
    send_mail(u'От бота артбелки', text, settings.EMAIL_FULL_ADDRESS, [shop_administrator_email])


class TextCommandEnum(object):
    GET_CATALOG = u'/get_catalog_'
    GET_PRODUCT = u'/get_it_'
    BACK = u'назад'
    FAQ = u'faq'


def get_request_data(request):
    if hasattr(request, 'request_data'):
        return request.request_data
    request_data = request.body.decode('utf-8')
    request.request_data = request_data
    return request_data