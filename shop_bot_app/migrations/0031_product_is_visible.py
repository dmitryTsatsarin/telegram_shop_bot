# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-03 22:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0030_bot_hello_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_visible',
            field=models.BooleanField(default=True, help_text='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0442\u043e\u0432\u0430\u0440 \u043f\u043e\u043a\u0443\u043f\u0430\u0442\u0435\u043b\u044e \u0438\u043b\u0438 \u043d\u0435\u0442'),
        ),
    ]
