# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-08-14 22:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0043_botbuyermap_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='botbuyermap',
            name='blocked_by_user',
            field=models.BooleanField(default=False),
        ),
    ]