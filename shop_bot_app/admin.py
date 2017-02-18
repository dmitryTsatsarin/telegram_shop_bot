from django.contrib import admin

# Register your models here.

from django.contrib import admin
from shop_bot_app.models import Product, Order, Customer, Feedback

class ProductAdmin(admin.ModelAdmin):
    pass

class OrderAdmin(admin.ModelAdmin):
    pass

class CustomerAdmin(admin.ModelAdmin):
    pass

class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ['customer']
    pass

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Feedback, FeedbackAdmin)