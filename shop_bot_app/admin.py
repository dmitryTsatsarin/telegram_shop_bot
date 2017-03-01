from django.contrib import admin

from shop_bot_app.models import Product, Order, Customer, Feedback, PostponedPost, PostponedPostResult, Catalog, BotAdministratorProfile


class ProductAdmin(admin.ModelAdmin):
    pass


class PostponedPostAdmin(admin.ModelAdmin):
    pass


class PostponedPostResultAdmin(admin.ModelAdmin):
    readonly_fields = ['is_sent', 'customer', 'postponed_post']


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['product', 'customer']


class CustomerAdmin(admin.ModelAdmin):
    pass


class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ['customer']


class CatalogAdmin(admin.ModelAdmin):
    pass


class BotAdministratorProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(PostponedPost, PostponedPostAdmin)
admin.site.register(PostponedPostResult, PostponedPostResultAdmin)
admin.site.register(Catalog, CatalogAdmin)
admin.site.register(BotAdministratorProfile, BotAdministratorProfileAdmin)
