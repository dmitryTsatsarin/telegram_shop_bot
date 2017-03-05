from django.contrib import admin

from shop_bot_app.models import Product, Order, Buyer, Feedback, PostponedPost, PostponedPostResult, Catalog, BotAdministratorProfile, Bot, BotBuyerMap, FAQ


class ProductAdmin(admin.ModelAdmin):
    pass


class PostponedPostAdmin(admin.ModelAdmin):
    pass


class PostponedPostResultAdmin(admin.ModelAdmin):
    readonly_fields = ['is_sent', 'buyer', 'postponed_post']


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['product', 'buyer']


class BuyerAdmin(admin.ModelAdmin):
    pass


class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ['buyer']


class CatalogAdmin(admin.ModelAdmin):
    pass


class BotAdministratorProfileAdmin(admin.ModelAdmin):
    pass


class BotAdmin(admin.ModelAdmin):
    readonly_fields = ['administrator']
    #exclude = ['is_bot_for_testing']


class BotBuyerMapAdmin(admin.ModelAdmin):
    pass


class FAQAdmin(admin.ModelAdmin):
    pass

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(PostponedPost, PostponedPostAdmin)
admin.site.register(PostponedPostResult, PostponedPostResultAdmin)
admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Bot, BotAdmin)
admin.site.register(BotBuyerMap, BotBuyerMapAdmin)
admin.site.register(FAQ, FAQAdmin)
