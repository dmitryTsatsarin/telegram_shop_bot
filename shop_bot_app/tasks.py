# -*- coding: utf-8 -*-
import logging

import arrow
import telebot as telebot_lib
from celery import shared_task

from shop_bot_app.bot_routing import initialize_bot_with_routing2
from shop_bot_app.logic import send_schedule_product
from shop_bot_app.models import Bot
from shop_bot_app.models import PostponedPost, Buyer, PostponedPostResult
from telegram_shop_bot.celery import app

logger = logging.getLogger(__name__)


@shared_task
def post_by_schedule():

    postponed_posts = list(PostponedPost.objects.filter(send_at__lte=arrow.now().datetime))
    # todo: опимизировать все в один запрос (но пока несрочно)
    for postponed_post in postponed_posts:
        buyers = list(Buyer.objects.filter(bot_buyer_map_rel__bot_id=postponed_post.product.bot_id).distinct())
        for buyer in buyers:
            if not PostponedPostResult.objects.filter(buyer=buyer, postponed_post=postponed_post).exists():
                send_schedule_product(buyer.telegram_user_id, postponed_post.product_id, postponed_post.description)
                PostponedPostResult.objects.create(buyer=buyer, postponed_post=postponed_post, is_sent=True)
                logger.info(u'Запущен PostponedPost с id=%s к buyer=(%s, %s)' % (postponed_post.id, buyer.id, buyer.full_name))



class CollectorTask(app.Task):
    queue = 'collector'

    def run(self, token, json_string, **kwargs):
        update = telebot_lib.types.Update.de_json(json_string)
        # Эта функция обеспечивает проверку входящего сообщения
        logger.info(u'data=%s' % json_string.decode('unicode-escape'))

        if Bot.objects.filter(telegram_token=token).exists():
            shop_telebot = initialize_bot_with_routing2(token)
            shop_telebot.process_new_updates([update])
        else:
            logger.error('Token "%s" is not found' % token)

