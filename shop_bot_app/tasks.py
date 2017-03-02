# -*- coding: utf-8 -*-
import logging

import arrow
from celery import shared_task

from shop_bot_app.logic import send_schedule_product
from shop_bot_app.models import PostponedPost, Buyer, PostponedPostResult

logger = logging.getLogger(__name__)


@shared_task
def post_by_schedule():

    postponed_posts = list(PostponedPost.objects.filter(send_at__lte=arrow.now().datetime))
    buyers = list(Buyer.objects.filter())
    # todo: опимизировать все в один запрос (но пока несрочно)
    for buyer in buyers:
        for postponed_post in postponed_posts:
            if not PostponedPostResult.objects.filter(buyer=buyer, postponed_post=postponed_post).exists():
                send_schedule_product(buyer.chat_id, postponed_post.product_id, postponed_post.description)
                PostponedPostResult.objects.create(buyer=buyer, postponed_post=postponed_post, is_sent=True)
                logger.info(u'Запущен PostponedPost с id=%s к buyer=(%s, %s)' % (postponed_post.id, buyer.id, buyer.full_name))
