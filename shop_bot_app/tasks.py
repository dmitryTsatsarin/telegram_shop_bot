# -*- coding: utf-8 -*-
import logging

import arrow
import telebot
from celery import shared_task
from django.conf import settings

from shop_bot_app.logic import send_schedule_product
from shop_bot_app.models import PostponedPost, Customer, PostponedPostResult
from shop_bot_app.utils import create_shop_telebot

logger = logging.getLogger(__name__)




@shared_task
def post_by_schedule():

    #todo: доделать эту часть !!!!!!!!!!!!!!!!!!! сделать выборку для каких ботов есть отложенные посты и отправить


    create_shop_telebot()

    postponed_posts = list(PostponedPost.objects.filter(send_at__lte=arrow.now().datetime))
    customers = list(Customer.objects.filter())
    # todo: опимизировать все в один запрос (но пока несрочно)
    for customer in customers:
        for postponed_post in postponed_posts:
            if not PostponedPostResult.objects.filter(customer=customer, postponed_post=postponed_post).exists():
                send_schedule_product(shop_telebot, customer.chat_id, postponed_post.product_id, postponed_post.description)
                PostponedPostResult.objects.create(customer=customer, postponed_post=postponed_post, is_sent=True)
                logger.info(u'Запущен PostponedPost с id=%s' % postponed_post.id)
