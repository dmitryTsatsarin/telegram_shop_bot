# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-01 23:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0015_auto_20170301_2352'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='bot',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='shop_bot_app.Bot'),
            preserve_default=False,
        ),
    ]