# -*- coding: utf-8 -*-
from urlparse import urlparse

from django.core.cache import cache
from django.core.files.images import ImageFile
from django.core.mail import send_mail
from django.http import QueryDict
from django.template import loader
from django.utils.http import urlencode
from telebot import types

from shop_bot_app.models import Bot

__author__ = 'forward'

import logging
logger = logging.getLogger(__name__)

from  shop_bot_app.utils import create_shop_telebot

from django.conf import settings


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


def send_mail_to_the_shop(order):

    shop_administrator_email = order.product.bot.order_email
    artbelka_administrator_email = settings.EMAIL_SHOP_BOT_ADMIN

    thumb_url = order.product.picture['400x400'].url

    context = {
        'order_id': order.id,
        'product_picture': "%s%s" % (settings.WEBSITE_BASE_URL, thumb_url),
        'product_name': order.product.name,
        'product_description': order.product.description,
        'product_price': order.product.price,
        'buyer_name': '%s %s' % (order.buyer.first_name, order.buyer.last_name),
        'buyer_phone': order.buyer.phone
    }

    html_message = loader.render_to_string('order_mail.html', context)
    text = ''
    logger.debug('Отправка письма')
    if shop_administrator_email:
        send_mail(u'От бота артбелки', text, settings.EMAIL_FULL_ADDRESS, [shop_administrator_email], html_message=html_message)
    else:
        logger.warning(u'Осуществлен заказ id=%s, но не указан email для заказов. Нужно срочно узнать кто владелец бота' % order.id)
    send_mail(u'От бота артбелки', text, settings.EMAIL_FULL_ADDRESS, [artbelka_administrator_email], html_message=html_message)
    logger.debug('письмо отправлено')


class TextCommandEnum(object):
    GET_CATALOG = u'/get_catalog'
    GET_PRODUCT = u'/get_it_'
    GET_PRODUCT_CONFIRM = u'/get_it2_'
    BACK = u'назад'
    FAQ = u'faq'
    SALE = u'распродажа'
    BACK_TO_PREVIOUS_CATALOG = u'back_to_previous_catalog'
    QUESTION_TO_ADMIN = u'задать вопрос'
    QUESTION_ABOUT_PRODUCT = u'/question_about_product'
    CLOSE_QUESTION_ABOUT_PRODUCT_DIALOG = u'закончить разговор'


class KeyValue(object):
    def __init__(self, cache_key, data_dict):
        self.cache_key = cache_key
        self._data = data_dict

    def __unicode__(self):
        return self.cache_key

    def __str__(self):
        return self.cache_key

    @property
    def data(self):
        return self._data

    def get_cache_key(self):
        return self.cache_key


# TODO: объединить эти 2 класса ####################################
class CacheKey(object):
    QUESTION_ABOUT_PRODUCT_ID = 'question_about_product_id'
    NEED_PHONE = 'need_phone'
    LAST_CATALOG_URI = 'last_catalog_uri'
    ORDER_ID = 'order_id'
    PRODUCT_ID = 'product_id'


class CacheKeyValue(object):
    QUESTION_MODE = KeyValue('question_mode', {
        'product_id': None,
        'is_buyer_notified': False
    })

# ####################################################################


class TsdRegExp(object):
    FIND_USER_IN_REPLY = '\(id=(\d+)\)'


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
    caption = u'%s\n%s\nТОРОПИТЕСЬ ТОВАР НА СКИДКЕ' % (product.name, product.description)

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


class CacheAsSession(object):
    chat_id = None

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def set(self, *arg, **kwargs):
        kwargs['version'] = kwargs.pop('chat_id', None) or self.chat_id
        return cache.set(*arg, **kwargs)

    def get(self, *arg, **kwargs):
        kwargs['version'] = kwargs.pop('chat_id', None) or self.chat_id
        return cache.get(*arg, **kwargs)

    def delete(self, *arg, **kwargs):
        kwargs['version'] = self.chat_id
        return cache.delete(*arg, **kwargs)

