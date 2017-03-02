# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    bot = models.ForeignKey('Bot')
    name = models.CharField(max_length=255)
    description = models.TextField()
    picture = models.ImageField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    catalog = models.ForeignKey('Catalog', null=True)
    is_discount = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class ChatIdBuyerMap(models.Model):
    buyer = models.ForeignKey('Buyer')




class Buyer(models.Model):
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=50, null=True)
    chat_id = models.BigIntegerField(null=True)

    @property
    def full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return u'%s %s %s' % (self.first_name, self.last_name, self.chat_id)


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
    title = models.CharField(max_length=100, verbose_name=u'Заголовок')
    description = models.TextField(verbose_name=u'Описание преложения/новости')
    product = models.ForeignKey(Product, verbose_name=u'Товар')
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
    administrator = models.ForeignKey(BotAdministratorProfile, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    telegram_token = models.CharField(max_length=255, null=True, blank=True)
    is_bot_for_testing = models.BooleanField(default=True)
    #telegram_token_test = models.CharField(max_length=255, null=True, blank=True, help_text=u'Токен телеграмма для тестрования')

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, *args, **kwargs):
        super(Bot, self).save(*args, **kwargs)

        from shop_bot_app.helpers import initialize_webhook_for_bot
        initialize_webhook_for_bot(self.telegram_token)


