# -*- coding: utf-8 -*-
from urlparse import urlparse
from django.http import QueryDict
from django.utils.http import urlencode
from django.core.mail import send_mail
from telebot import types

from shop_bot_app.models import Bot
from django.core.files.images import ImageFile

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


def initialize_one_webhook(bot_name):
    print 'Инициализация начата'
    bot = Bot.objects.filter(name=bot_name).get()
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
    GET_CATALOG = u'/get_catalog'
    GET_PRODUCT = u'/get_it_'
    BACK = u'назад'
    FAQ = u'faq'
    SALE = u'распродажа'


class CacheKey(object):
    QUESTION_TO_ADMIN = 'question_to_admin'
    NEED_PHONE = 'need_phone'


class Smile(object):
    SMILING_FACE_WITH_SMILING_EYE = u"\U0001F60A"


def get_request_data(request):
    if hasattr(request, 'request_data'):
        return request.request_data
    request_data = request.body.decode('utf-8')
    request.request_data = request_data
    return request_data



def generate_and_send_discount_product(product, shop_telebot, message):
    image_file = ImageFile(product.picture)
    order_command = u'/get_it_%s' % product.id
    caption = u'%s\n%s\n%s\nТОРОПИТЕСЬ ТОВАР НА СКИДКЕ' % (product.name, product.description, product.price)

    markup = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
    markup.add(callback_button)

    shop_telebot.send_photo(message.chat.id, image_file, caption=caption, reply_markup=markup)


def get_query_dict(uri):
    if '?' in uri:
        query_dict = QueryDict(urlparse(uri).query)
    else:
        query_dict = QueryDict(uri)
    return query_dict


def create_uri(url, **params):
    return "%s?%s" % (url, urlencode(params))

