# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-24 23:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0028_auto_20170325_0139'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='order_email',
            field=models.EmailField(help_text='\u0421\u044e\u0434\u0430 \u0431\u0443\u0434\u0435\u0442 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u0442\u044c\u0441\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e \u0437\u0430\u043a\u0430\u0437\u0435', max_length=254, null=True),
        ),
    ]
