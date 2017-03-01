from __future__ import unicode_literals

from time import sleep

from django.apps import AppConfig


class ShopBotAppConfig(AppConfig):
    name = 'shop_bot_app'

    def ready(self):
        pass

