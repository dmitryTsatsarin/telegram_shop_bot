# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-27 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0029_bot_order_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='hello_description',
            field=models.CharField(default='', help_text='\u041d\u0430\u0447\u0430\u043b\u044c\u043d\u043e\u0435 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043f\u043e\u0441\u043b\u0435 /start', max_length=1000),
        ),
    ]
