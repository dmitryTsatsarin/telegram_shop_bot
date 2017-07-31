# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.contrib import admin

from easy_thumbnails.widgets import ImageClearableFileInput
from easy_thumbnails.fields import ThumbnailerField

from shop_bot_app.models import Product, Order, Buyer, Feedback, PostponedPost, PostponedPostResult, Catalog, BotAdministratorProfile, Bot, BotBuyerMap, FAQ, MessageLog


class GetBotMixin(object):

    def get_bot(self, request):
        # выделено в отдельный метод, т.к. мы работаем с одним пользователем на бота, а в будущем пока не понятно
        bot = Bot.objects.filter(administrator=request.user).get()
        return bot


class CustomModelAdmin(admin.ModelAdmin, GetBotMixin):
    exclude = ['bot']

    def save_model(self, request, obj, form, change):
        obj.bot = self.get_bot(request)
        return super(CustomModelAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(CustomModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        bot = self.get_bot(request)
        return qs.filter(bot=bot)

    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomModelAdmin, self).get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            bot = self.get_bot(request)
            if form.base_fields.get('catalog'):
                form.base_fields['catalog'].queryset = Catalog.objects.filter(bot=bot)
            if form.base_fields.get('product'):
                form.base_fields['product'].queryset = Product.objects.filter(bot=bot)
        return form


class ProductAdmin(CustomModelAdmin):
    list_display = ['name', 'id', 'is_visible', 'description', 'vendor_code', 'catalog']
    fields = ('name', 'description', 'picture', 'catalog', 'is_discount', 'is_visible', 'vendor_code')

    formfield_overrides = {
        ThumbnailerField: {'widget': ImageClearableFileInput },
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super(self.__class__, self).get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            bot = self.get_bot(request)
            form.base_fields['catalog'].queryset = Catalog.objects.filter(bot=bot)
        return form


class PostponedPostAdmin(CustomModelAdmin):

    formfield_overrides = {
        ThumbnailerField: {'widget': ImageClearableFileInput},
    }



class PostponedPostResultAdmin(admin.ModelAdmin):
    readonly_fields = ['is_sent', 'buyer', 'postponed_post']


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['product', 'buyer']


class BuyerAdmin(admin.ModelAdmin):
    pass


class FeedbackAdmin(CustomModelAdmin):

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'readonly':'readonly'})}
    }
    readonly_fields = ['buyer']
    # на данный момент нельзя сделать фейковый фидбек через админку, что правильно. Пока сделал через read only,может придумать что-нибудь другое


class CatalogAdmin(CustomModelAdmin):
    list_display = ['name', 'id']


class BotAdministratorProfileAdmin(admin.ModelAdmin):
    pass


class BotAdminForm(forms.ModelForm):
    hello_description = forms.CharField(widget=forms.Textarea, help_text='Начальное описание после /start')

    class Meta:
        model = Bot
        fields = ['name', 'telegram_token', 'order_email', 'hello_description', 'bot_support']


class BotAdmin(admin.ModelAdmin):
    form = BotAdminForm
    readonly_fields = ['administrator']

    def get_queryset(self, request):
        qs = super(BotAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(administrator=request.user)



class BotBuyerMapAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'dialog_with_support']


class FAQAdminForm(forms.ModelForm):
    answer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'picture']


class FAQAdmin(CustomModelAdmin):
    form = FAQAdminForm

    # непонятно почему не работает, если указывать ThumbnailerField и widget=ImageClearableFileInput в форме ((((((
    formfield_overrides = {
        ThumbnailerField: {'widget': ImageClearableFileInput},
    }


class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'message_text', 'created_at', 'buyer', 'bot']

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
admin.site.register(MessageLog, MessageLogAdmin)
