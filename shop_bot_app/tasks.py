# -*- coding: utf-8 -*-
import logging

import arrow
import telebot as telebot_lib
from celery import shared_task
from django.conf import settings

from shop_bot_app.bot_routing import initialize_bot_with_routing2
from shop_bot_app.logic import send_schedule_product
from shop_bot_app.models import Bot
from shop_bot_app.models import PostponedPost, Buyer, PostponedPostResult
from telegram_shop_bot.celery import app
from telebot import apihelper
import json

import botan

logger = logging.getLogger(__name__)


@shared_task
def post_by_schedule():

    postponed_posts = list(PostponedPost.objects.filter(send_at__lte=arrow.now().datetime))
    # todo: опимизировать все в один запрос (но пока несрочно)
    for postponed_post in postponed_posts:
        buyers = list(Buyer.objects.filter(bot_buyer_map_rel__bot_id=postponed_post.bot_id).distinct())
        for buyer in buyers:
            if not PostponedPostResult.objects.filter(buyer=buyer, postponed_post=postponed_post).exists():
                try:
                    send_schedule_product(buyer.telegram_user_id, postponed_post)
                    PostponedPostResult.objects.create(buyer=buyer, postponed_post=postponed_post, is_sent=True)
                    logger.info(u'Запущен PostponedPost с id=%s к buyer=(%s, %s)' % (postponed_post.id, buyer.id, buyer.full_name))
                except apihelper.ApiException as e:
                    error_msg = 'Forbidden: bot was blocked by the user'
                    if e.result.status_code == 403 and error_msg in e.result.text:
                        msg = u'Пользователь %s (id=%s) заблокировал бота' % (buyer.full_name, buyer.telegram_user_id)
                        logger.info(msg)


class CollectorTask(app.Task):
    queue = 'collector'

    def _custom_de_json(self, json_string):
        try:
            data_dict = json.loads(json_string)
        except ValueError as e:
            data_dict = {}
        return data_dict

    def run(self, token, json_string, message_created_at, **kwargs):
        try:
            update = telebot_lib.types.Update.de_json(json_string)
            update.sys_message_created_at = message_created_at
            update.sys_message_received_at = arrow.now().datetime
            request_dict = self._custom_de_json(json_string)
            logger.info(u'data=%s' % json_string.decode('unicode-escape'))

            if update.callback_query:
                chat_id = update.callback_query.message.chat.id
                event_name = update.callback_query.data
            elif update.message:
                chat_id = update.message.chat.id
                event_name = update.message.text
            elif request_dict.has_key('channel_post') or request_dict.has_key('edited_channel_post'):
                # пока игнорируем сообщения из каналов
                logger.info(u'Проигнорировано сообщение из channel %s' % json_string.decode('unicode-escape'))
                return
            else:
                raise Exception('chat_id is not found')

            if Bot.objects.filter(telegram_token=token).exists():
                MetricTask().apply_async(args=[chat_id, request_dict, event_name])
                shop_telebot = initialize_bot_with_routing2(token, chat_id)
                shop_telebot.process_new_updates([update])
            else:
                logger.error('Token "%s" is not found' % token)
        except Exception as e:
            if settings.DEBUG:
                logger.debug(e, exc_info=True)
            else:
                logger.exception(e)
                raise


class MetricTask(app.Task):
    queue = 'metric'

    def run(self, uid, message_dict, event_name, **kwargs):
        try:
            # uid = message.from_user
            # message_dict = message.to_dict()
            # event_name = update.message.text

            result = botan.track(settings.BOTAN_TOKEN, uid, message_dict, event_name)
            if result and result['status'] and 'accepted' not in result['status']:
                logger.warning('Something wrong with metrics: %s' % result)
            logger.info(result)

        except Exception as e:
            if settings.DEBUG:
                logger.debug(e, exc_info=True)
            else:
                logger.exception(e)
                raise
