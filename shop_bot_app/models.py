from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    picture = models.ImageField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
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