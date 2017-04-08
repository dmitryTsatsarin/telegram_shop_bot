# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from os.path import splitext
import uuid

from easy_thumbnails.fields import ThumbnailerImageField


def rename_and_upload_path(instance, filename):
    _, ext = splitext(filename)

    base_filename = str(uuid.uuid4())

    return 'product_photo/%s%s' % (base_filename, ext)



class Product(models.Model):
    bot = models.ForeignKey('Bot')
    name = models.CharField(max_length=255)
    description = models.TextField()
    picture = ThumbnailerImageField(upload_to=rename_and_upload_path)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    catalog = models.ForeignKey('Catalog', null=True)
    is_discount = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True, help_text='Показывать товар покупателю или нет')

    def __unicode__(self):
        return self.name

    def get_400x400_picture_file(self):
        image_file = open(self.picture['400x400'].path)
        return image_file


class BotBuyerMap(models.Model):
    buyer = models.ForeignKey('Buyer', related_name='bot_buyer_map_rel')
    bot = models.ForeignKey('Bot', related_name='bot_buyer_map_rel')

    def __unicode__(self):
        return u'%s <-> %s' % (self.bot.name, self.buyer.full_name)


class Buyer(models.Model):
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=50, null=True)
    telegram_user_id = models.BigIntegerField(null=True)

    @property
    def full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return u'%s %s %s' % (self.first_name, self.last_name, self.telegram_user_id)


class Order(models.Model):
    product = models.ForeignKey(Product)
    buyer = models.ForeignKey(Buyer)

    def __unicode__(self):
        return u'%s' % self.id


class Feedback(models.Model):
    bot = models.ForeignKey('Bot')
    buyer = models.ForeignKey(Buyer)
    description = models.TextField()
    created_at= models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.description


class PostponedPost(models.Model):
    bot = models.ForeignKey('Bot')
    title = models.CharField(max_length=100, verbose_name=u'Заголовок')
    description = models.TextField(verbose_name=u'Описание преложения/новости')
    product = models.ForeignKey(Product, verbose_name=u'Товар', null=True, blank=True)
    send_at = models.DateTimeField(verbose_name=u'Отправить в')
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.title


class PostponedPostResult(models.Model):
    buyer = models.ForeignKey(Buyer)
    postponed_post = models.ForeignKey(PostponedPost)
    is_sent = models.BooleanField(default=False, verbose_name=u'Отправлено')
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.id


class Catalog(models.Model):
    bot = models.ForeignKey('Bot')
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % self.name


class BotAdministratorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return u'%s' % self.user.username


class Bot(models.Model):
    administrator = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    telegram_token = models.CharField(max_length=255, null=True, blank=True)
    order_email = models.EmailField(null=True, help_text='Сюда будет отправляться информация о заказе')
    bot_support = models.ForeignKey(Buyer, null=True, help_text='Человек, которому будут перенаправляться все вопросы из бота')
    hello_description = models.CharField(max_length=1000, default='', help_text='Начальное описание после /start')
    #is_bot_for_testing = models.BooleanField(default=True)
    #telegram_token_test = models.CharField(max_length=255, null=True, blank=True, help_text=u'Токен телеграмма для тестрования')

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, *args, **kwargs):
        group_name = 'bot_administrator_group'
        group = Group.objects.filter(name=group_name).get()
        if not self.administrator:
            username = '%s%s' % (self.name, 'Administrator')
            password = User.objects.make_random_password()
            user = User.objects.create_user(username=username, password=password, is_staff=True)
            BotAdministratorProfile.objects.create(user_id=user.id)
            user.groups.add(group)
            self.administrator = user

        super(Bot, self).save(*args, **kwargs)

        from shop_bot_app.helpers import initialize_webhook_for_bot
        initialize_webhook_for_bot(self.telegram_token)


class FAQ(models.Model):
    bot = models.ForeignKey(Bot)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=1000)


    def __unicode__(self):
        return u'%s' % self.question
