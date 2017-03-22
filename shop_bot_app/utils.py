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
        def dont_response_on_old_request(message):
            last_request_at = cache.get('last_request_at', version=message.chat.id)
            if last_request_at <= message.date or not last_request_at:
                cache.set('last_request_at', message.date, version=message.chat.id)
                super(ShopTeleBot, self)._exec_task(*args, **kwargs)
            else:
                logger.info(u'Request has old time %s. Current = %s. Ignored' % (message.date, last_request_at))

        instance = args[1]
        if hasattr(instance, 'message'):
            message = instance.message
        else:
            message = instance
        # временно отключено, так как блокировало по нажатию на старые кнопки. От спама в текущей реализации не спасает. Подумать о другом варианте
        #dont_response_on_old_request(message)

        super(ShopTeleBot, self)._exec_task(*args, **kwargs)


def create_shop_telebot(token):
    bot = ShopTeleBot(token)
    return bot

