# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import telebot
from django.conf import settings

from shop_bot_app.helpers import initialize_all_webhooks, initialize_one_webhook


class Command(BaseCommand):
    # help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--bot_name',  action='store', dest='bot_name')

    def handle(self, *args, **options):
        bot_name = options['bot_name']
        if bot_name:
            initialize_one_webhook(bot_name)
        else:
            raise Exception('Need "bot_name" parameter')
