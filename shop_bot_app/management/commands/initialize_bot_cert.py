# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import telebot
from django.conf import settings

from shop_bot_app.helpers import initialize_bot_cert


class Command(BaseCommand):
    # help = "My shiny new management command."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):

        initialize_bot_cert()
