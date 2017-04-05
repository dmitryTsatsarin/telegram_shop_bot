# -*- coding: utf-8 -*-
__author__ = 'forward'

from django.conf.urls import include, url

from shop_bot_app.views import webhooks, main_page

urlpatterns = [
    url(r'^(?P<token>.+:.+)/$', webhooks),
]