# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-04 11:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0019_auto_20170303_0209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bot',
            name='is_bot_for_testing',
        ),
    ]