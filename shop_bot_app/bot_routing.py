# -*- coding: utf-8 -*-
from shop_bot_app.helpers import TextCommandEnum, CacheKey

__author__ = 'forward'
from shop_bot_app import logic
from django.core.cache import cache


def initialize_bot_with_routing2(token):

    bv = logic.BotView(token)

    def if_it_is_question_to_administrator(message):
        result = bool(cache.get(CacheKey.QUESTION_TO_ADMIN, version=message.chat.id))
        if result:
            cache.delete(CacheKey.QUESTION_TO_ADMIN, version=message.chat.id)
        return result

    bv.shop_telebot.simple_message_handler(commands=['start', ], handler=bv.handle_start_help)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.FAQ), content_types=['text'], handler=bv.handle_faq)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(u'каталог'), content_types=['text'], handler=bv.handle_catalog)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.GET_CATALOG), handler=bv.handle_show_catalog_products)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.SALE), content_types=['text'], handler=bv.handle_catalog_discount)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.SALE), handler=bv.handle_more_catalog_discount_products)
    bv.shop_telebot.simple_message_handler(content_types=['contact'], handler=bv.handle_contact)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(u'/get_it_'), handler=bv.callback_catalog_order)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.BACK), content_types=['text'], handler=bv.handle_send_message_to_administator_preview_back)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(u'задать вопрос'), content_types=['text'], handler=bv.handle_send_message_to_administator_preview)
    bv.shop_telebot.simple_message_handler(func=if_it_is_question_to_administrator, content_types=['text'], handler=bv.handle_send_message_to_administator)
    bv.shop_telebot.simple_message_handler(content_types=['text'], handler=bv.handle_default)

    return bv.shop_telebot





