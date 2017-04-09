# -*- coding: utf-8 -*-
__author__ = 'forward'
from telebot import TeleBot
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class ShopTeleBot(TeleBot, object):
    def __init__(self, token, threaded=False, skip_pending=False):
        # треды выключил по умолчанию
        super(ShopTeleBot, self).__init__(token, threaded=threaded, skip_pending=skip_pending)

    def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None,
                     parse_mode=None, disable_notification=None):
        result = super(ShopTeleBot, self).send_message(chat_id, text, disable_web_page_preview=disable_web_page_preview, reply_to_message_id=reply_to_message_id, reply_markup=reply_markup,
                     parse_mode=parse_mode, disable_notification=disable_notification)
        # может в будущем добавить логивароние ответов
        #logger.info('LOGGER: %s' % text)
        return result

    def send_photo(self, *args, **kwargs):
        result = super(ShopTeleBot, self).send_photo(*args, **kwargs)
        print 'Send photo is finished'
        return result

    def simple_message_handler(self, commands=None, regexp=None, func=None, content_types=None, handler=None, **kwargs):
        if not content_types:
            content_types = ['text']


        handler_dict = self._build_handler_dict(handler,
                                                commands=commands,
                                                regexp=regexp,
                                                func=func,
                                                content_types=content_types,
                                                **kwargs)

        self.add_message_handler(handler_dict)

    def simple_callback_query_handler(self, func, handler=None, **kwargs):
        handler_dict = self._build_handler_dict(handler, func=func, **kwargs)
        self.add_callback_query_handler(handler_dict)

    def _exec_task(self, *args, **kwargs):

        def log_message_text(message):
            logger.info(u'LOGGER: %s' % message.text)

        instance = args[1]
        if hasattr(instance, 'message'):
            message = instance.message
        else:
            message = instance

        # временно отключено, так как блокировало по нажатию на старые кнопки. От спама в текущей реализации не спасает. Подумать о другом варианте
        #dont_response_on_old_request(message)

        # может в будущем делать логивароние всех запросов пользователя, но пока это лишнее
        #log_message_text(message)

        super(ShopTeleBot, self)._exec_task(*args, **kwargs)


def create_shop_telebot(token):
    bot = ShopTeleBot(token)
    return bot

