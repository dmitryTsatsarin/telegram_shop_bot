# -*- coding: utf-8 -*-
from shop_bot_app.helpers import TextCommandEnum, CacheKey, CacheKeyValue, TsdRegExp

__author__ = 'forward'

import re
from shop_bot_app import logic
from django.core.cache import cache


def initialize_bot_with_routing2(token, chat_id):

    bv = logic.BotView(token, chat_id)

    def if_is_it_qestion_mode(message):
        result = bv.pseudo_session.get(CacheKeyValue().QUESTION_MODE)
        return bool(result)

    def if_need_phone(message):
        is_need_phone = bool(cache.get(CacheKey.NEED_PHONE, version=message.chat.id))
        if is_need_phone:
            cache.delete(CacheKey.NEED_PHONE, version=message.chat.id)
        return is_need_phone

    def if_is_admin_answer_to_buyer(message):
        if message and message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
            return bool(re.search(TsdRegExp.FIND_USER_IN_REPLY, text))
        return False


    bv.shop_telebot.simple_message_handler(commands=['start', ], handler=bv.handle_start_help)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.FAQ), content_types=['text'], handler=bv.handle_faq)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(u'каталог'), content_types=['text'], handler=bv.handle_catalog)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.GET_CATALOG), handler=bv.handle_show_catalog_products)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.SALE), content_types=['text'], handler=bv.handle_catalog_discount)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.SALE), handler=bv.handle_more_catalog_discount_products)
    #bv.shop_telebot.simple_message_handler(content_types=['contact'], handler=bv.handle_contact)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.GET_PRODUCT_CONFIRM), handler=bv.handle_need_to_enter_phone)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.GET_PRODUCT), handler=bv.callback_catalog_order)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.BACK_TO_PREVIOUS_CATALOG), handler=bv.handle_back_to_previous_catalog)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.BACK), content_types=['text'], handler=bv.handle_send_message_to_administator_preview_back)

    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.QUESTION_TO_ADMIN), content_types=['text'], handler=bv.handle_send_message_to_administator_preview)
    bv.shop_telebot.simple_callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.QUESTION_ABOUT_PRODUCT), handler=bv.handle_start_question_about_product)
    bv.shop_telebot.simple_message_handler(func=lambda message: message.text.lower().startswith(TextCommandEnum.CLOSE_QUESTION_ABOUT_PRODUCT_DIALOG), content_types=['text'], handler=bv.handle_close_question_dialog)
    bv.shop_telebot.simple_message_handler(func=if_is_it_qestion_mode, content_types=['text'], handler=bv.handle_question_to_bot_support)
    bv.shop_telebot.simple_message_handler(func=if_is_admin_answer_to_buyer, content_types=['text'], handler=bv.handle_question_about_product_admin_say)

    bv.shop_telebot.simple_message_handler(func=if_need_phone, content_types=['text'], handler=bv.handle_need_phone)

    bv.shop_telebot.simple_message_handler(content_types=['text'], handler=bv.handle_default)

    return bv.shop_telebot





