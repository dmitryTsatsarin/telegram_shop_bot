# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-20 20:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop_bot_app', '0009_auto_20170220_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotAdministratorProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_token', models.CharField(max_length=255)),
                ('telegram_token_test', models.CharField(help_text='\u0422\u043e\u043a\u0435\u043d \u0442\u0435\u043b\u0435\u0433\u0440\u0430\u043c\u043c\u0430 \u0434\u043b\u044f \u0442\u0435\u0441\u0442\u0440\u043e\u0432\u0430\u043d\u0438\u044f', max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
