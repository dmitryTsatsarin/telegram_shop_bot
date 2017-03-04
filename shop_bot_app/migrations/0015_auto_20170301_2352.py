# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-01 23:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0014_auto_20170301_2225'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='bot',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='shop_bot_app.Bot'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='bot',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='shop_bot_app.Bot'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bot',
            name='administrator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop_bot_app.BotAdministratorProfile'),
        ),
    ]