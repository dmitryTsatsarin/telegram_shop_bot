# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    picture = models.ImageField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    catalog = models.ForeignKey('Catalog', null=True)
    is_discount = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=50, null=True)
    chat_id = models.BigIntegerField(null=True)

    def __unicode__(self):
        return u'%s %s %s' % (self.first_name, self.last_name, self.chat_id)


class Order(models.Model):
    product = models.ForeignKey(Product)
    customer = models.ForeignKey(Customer)

    def __unicode__(self):
        return u'%s' % self.id


class Feedback(models.Model):
    customer = models.ForeignKey(Customer)
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
    customer = models.ForeignKey(Customer)
    postponed_post = models.ForeignKey(PostponedPost)
    is_sent = models.BooleanField(default=False, verbose_name=u'Отправлено')
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.id


class Catalog(models.Model):
    name = models.CharField(max_length=100)


class BotAdministratorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_token = models.CharField(max_length=255, null=True, blank=True)
    telegram_token_test = models.CharField(max_length=255, null=True, blank=True, help_text=u'Токен телеграмма для тестрования')

    def __unicode__(self):
        return u'%s' % self.user.username
