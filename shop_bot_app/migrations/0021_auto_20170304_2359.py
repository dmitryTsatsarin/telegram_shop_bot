# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-04 20:59
from __future__ import unicode_literals

from django.db import migrations, models
import shop_bot_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_bot_app', '0020_remove_bot_is_bot_for_testing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='picture',
            field=models.ImageField(upload_to=shop_bot_app.models.rename_and_upload_path),
        ),
    ]
