# -*- coding: utf-8 -*-
import logging
import re

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from telebot import types

from shop_bot_app.helpers import TextCommandEnum, send_mail_to_the_shop, generate_and_send_discount_product, get_query_dict, create_uri, CacheKey, Smile, CacheAsSession, CacheKeyValue, \
    TsdRegExp
from shop_bot_app.models import Product, Buyer, Order, Feedback, Bot, Catalog, BotBuyerMap, FAQ
from shop_bot_app.utils import create_shop_telebot

logger = logging.getLogger(__name__)
to_log = logger.info


def send_schedule_product(telegram_user_id, postponed_post):
    product_id = postponed_post.product_id
    post_description = postponed_post.description

    shop_telebot = create_shop_telebot(postponed_post.bot.telegram_token)
    if product_id:
        product = Product.objects.filter(id=product_id).get()

        image_file = product.get_400x400_picture_file()

        order_command = u'/get_it_%s' % product.id
        caption = u'%s\nНаименование: %s\nОписание: %s\nЦена: %s' % (post_description, product.name, product.description, product.price)

        markup = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
        markup.add(callback_button)

        shop_telebot.send_photo(telegram_user_id, image_file, caption=caption, reply_markup=markup, disable_notification=True)
    else:
        shop_telebot.send_message(telegram_user_id, text=post_description, disable_notification=True)


class BotView(object):
    shop_telebot = None
    menu_markup = None
    token = None
    bot_id = None

    def __init__(self, token, chat_id):
        self.token = token
        menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menu_markup.row(u'Каталог', u'Распродажа %')
        menu_markup.row(u'Помощь', u'Задать вопрос')
        self.menu_markup = menu_markup

        close_product_dialog_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        close_product_dialog_markup.row(u'Закончить разговор')
        self.close_product_dialog_markup = close_product_dialog_markup

        shop_telebot = create_shop_telebot(token)
        self.shop_telebot = shop_telebot
        self.chat_id = chat_id
        self.pseudo_session = CacheAsSession(chat_id)

        bot = Bot.objects.get(telegram_token=token)
        self.bot_id = bot.id
        self.bot_support_chat_id = None
        if bot.bot_support:
            self.bot_support_chat_id = bot.bot_support.telegram_user_id

    # Обработчик команд '/start'
    def handle_start_help(self, message):
        telegram_user_id = message.chat.id
        # create buyer
        bot = Bot.objects.filter(telegram_token=self.token).get()
        try:
            BotBuyerMap.objects.filter(buyer__telegram_user_id=telegram_user_id, bot=bot).get()
        except BotBuyerMap.DoesNotExist as e:
            first_name = message.chat.first_name or ''
            last_name = message.chat.last_name or ''
            buyer, _ = Buyer.objects.get_or_create(telegram_user_id=telegram_user_id, defaults=dict(
                        first_name=first_name,
                        last_name=last_name,
                        telegram_user_id=telegram_user_id
                )
            )
            BotBuyerMap.objects.create(bot=bot, buyer=buyer)

        text_out = bot.hello_description
        self.shop_telebot.send_message(message.chat.id, text_out, parse_mode='markdown')

        self.shop_telebot.send_message(message.chat.id, "Сделайте ваш выбор:", reply_markup=self.menu_markup)

    def handle_faq(self, message):
        faqs = list(FAQ.objects.filter(bot_id=self.bot_id))
        if faqs:
            for faq in faqs:
                question = faq.question
                answer = faq.answer
                text_out = u'%s\n%s' % (question, answer)
                self.shop_telebot.send_message(message.chat.id, text_out)
        else:
            self.shop_telebot.send_message(message.chat.id, u'Раздел помощи пуст')

    def handle_catalog(self, message):
        catalogs = list(Catalog.objects.filter(bot_id=self.bot_id))
        markup = types.InlineKeyboardMarkup()
        if catalogs:
            for catalog in catalogs:
                order_command = u'/get_catalog?catalog_id=%s' % catalog.id
                products_count = Product.objects.filter(catalog_id=catalog.id, bot_id=self.bot_id, is_visible=True).count()
                text = u'%s (%s)' % (catalog.name, products_count)
                callback_button = types.InlineKeyboardButton(text=text, callback_data=order_command)
                markup.add(callback_button)
            self.shop_telebot.send_message(message.chat.id, 'Каталоги', reply_markup=markup)
        else:
            self.shop_telebot.send_message(message.chat.id, 'Каталогов нет :(', reply_markup=markup)

    def handle_show_catalog_products(self, call, indirect_call=None):
        limit = 5

        call_data = indirect_call if indirect_call else call.data
        query_dict = get_query_dict(call_data)
        catalog_id_str = query_dict.get('catalog_id')
        catalog_id = int(catalog_id_str) if catalog_id_str else None
        offset = int(query_dict.get('offset', 0))

        if not catalog_id:
            logger.error(u'Каталог не найден (%s)' % call_data)
            self.shop_telebot.send_message(self.chat_id, u'Неккорректная ссылка каталога, выберете другой каталог')
            return

        self.pseudo_session.set(CacheKey.LAST_CATALOG_URI, call_data)

        queryset = Product.objects.filter(bot_id=self.bot_id, catalog_id=catalog_id, is_visible=True).order_by('-id')
        product_count = queryset.count()

        products = list(queryset[offset:offset + limit])
        # todo: возможно стоит вынести общую часть в отдельные функции
        for product in products:
            image_file = product.get_400x400_picture_file()
            order_command = u'%s%s' % (TextCommandEnum.GET_PRODUCT, product.id)
            caption = u'%s\n%s' % (product.name, product.description)

            markup = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)

            # пока не нужно, или удалить потом, или еще что
            # product_question_command = create_uri(TextCommandEnum.QUESTION_ABOUT_PRODUCT, product_id=product.id)
            # product_question_button = types.InlineKeyboardButton(text=u"Задать вопрос по товару", callback_data=product_question_command)
            # markup.add(product_question_button)

            markup.add(callback_button)
            self.shop_telebot.send_photo(self.chat_id, image_file, caption=caption, reply_markup=markup)
        if product_count > offset + limit:
            new_offset = offset + limit
            more_command = create_uri(TextCommandEnum.GET_CATALOG, catalog_id=catalog_id, offset=new_offset)
            markup = types.InlineKeyboardMarkup()
            rest_amount = product_count - new_offset
            callback_button = types.InlineKeyboardButton(text=u"Показать еще 5 ( %s не показано)" % rest_amount, callback_data=more_command)
            markup.add(callback_button)
            self.shop_telebot.send_message(self.chat_id, u'Показать другие товары?', reply_markup=markup)
        if not products:
            self.shop_telebot.send_message(self.chat_id, u'Каталог пуст')

    def core_handle_more_catalog_discount_products(self, message, data=None):
        limit = 5

        if data:
            query_dict = get_query_dict(data)
            offset = int(query_dict.get('offset', 0))
        else:
            offset = 0

        queryset = Product.objects.filter(bot_id=self.bot_id, is_discount=True, is_visible=True).order_by('-id')
        product_count = queryset.count()

        products = list(queryset[offset:offset + limit])
        for product in products:
            generate_and_send_discount_product(product, self.shop_telebot, message)

        if product_count > offset + limit:
            new_offset = offset + limit
            more_command = create_uri(TextCommandEnum.SALE, offset=new_offset)
            markup = types.InlineKeyboardMarkup()
            rest_amount = product_count - new_offset
            callback_button = types.InlineKeyboardButton(text=u"Показать еще 5 ( %s не показано)" % rest_amount, callback_data=more_command)
            markup.add(callback_button)
            self.shop_telebot.send_message(message.chat.id, u'Показать другие товары?', reply_markup=markup)

        if not products:
            self.shop_telebot.send_message(message.chat.id, u'Нет товара на скидке')

    def handle_catalog_discount(self, message):
        return self.core_handle_more_catalog_discount_products(message)

    def handle_more_catalog_discount_products(self, call):
        return self.core_handle_more_catalog_discount_products(call.message, call.data)

    #
    # def handle_contact(self, message):
    #     phone_number = message.contact.phone_number
    #     buyer = Buyer.objects.filter(telegram_user_id=message.chat.id).get()
    #     buyer.phone = phone_number
    #     buyer.save()
    #
    #     order_id = cache.get('order', version=message.chat.id)
    #     order = Order.objects.get(id=order_id)
    #
    #     text_out = u'Спасибо, ваши контакты (%s) были отправлены менеджеру компании. Ожидайте он свяжется с вами' % phone_number
    #     self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)
    #
    #     send_mail_to_the_shop(order)

    def callback_catalog_order(self, call):
        logger.debug('Оформление заказа')
        buyer = Buyer.objects.filter(telegram_user_id=call.message.chat.id).get()
        product_id = int(call.data.lower().replace(u'/get_it_', ''))
        product = Product.objects.filter(id=product_id).get()

        # дублирование отображения выбранного товара
        text_out = 'Вы хотите заказать:'
        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.menu_markup)
        image_file = product.get_400x400_picture_file()
        caption = u'%s\n%s' % (product.name, product.description)
        markup = types.InlineKeyboardMarkup()
        cancel_callback_button = types.InlineKeyboardButton(text=u"Отменить заказ", callback_data=TextCommandEnum.BACK_TO_PREVIOUS_CATALOG)
        confirm_order_command = create_uri(TextCommandEnum.GET_PRODUCT_CONFIRM, product_id=product_id)
        confirm_callback_button = types.InlineKeyboardButton(text=u"Подтвердить заказ", callback_data=confirm_order_command)
        markup.add(cancel_callback_button)
        markup.add(confirm_callback_button)
        self.shop_telebot.send_photo(call.message.chat.id, image_file, caption=caption, reply_markup=markup)

        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # phone_btn = types.KeyboardButton(u'отправить номер телефона', request_contact=True)
        # back_btn = types.KeyboardButton(u'Назад')
        # markup.add(phone_btn)
        # markup.add(back_btn)
        # cache.set(CacheKey.NEED_PHONE, True, version=call.message.chat.id)
        # text_out = u'*Заказ оформлен* (%s).\n\n Укажите ваш номер телефона и менеджер вам перезвонит' % product.name
        # self.shop_telebot.send_message(call.message.chat.id, text_out, reply_markup=markup, parse_mode='markdown')

    def handle_need_to_enter_phone(self, call):
        query_dict = get_query_dict(call.data)
        product_id = query_dict.get('product_id')
        if product_id:
            self.pseudo_session.set(CacheKey.PRODUCT_ID, product_id)
            text_out = u'Введите ваш номер телефона в формате "код_оператора телефон". Пример: 29 1234567'
            self.shop_telebot.send_message(self.chat_id, text_out)
            self.pseudo_session.set(CacheKey.NEED_PHONE, True)
        else:
            text_out = u'Похоже либо вы выбрали товар, либо у нас произошел сбой. Попробуйте повторить'
            self.shop_telebot.send_message(self.chat_id, text_out)

    def handle_back_to_previous_catalog(self, call):
        text_out = u'Возврат к товарам'
        self.shop_telebot.send_message(call.message.chat.id, text_out, reply_markup=self.menu_markup)
        last_catalog_uri = self.pseudo_session.get(CacheKey.LAST_CATALOG_URI)
        self.handle_show_catalog_products(None, indirect_call=last_catalog_uri)

    def handle_send_message_to_administator_preview_back(self, message):
        text_out = u'Возврат в начало'
        self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)

    def handle_send_message_to_administator_preview(self, message):
        text_out = u'Задайте вопрос администратору:'
        self._start_question_dialog(message)
        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.close_product_dialog_markup)

    def handle_need_phone(self, message):
        matched_result = re.search(u'[^\+\s\(\)\d]+', message.text)
        if matched_result:
            self.pseudo_session.set(CacheKey.NEED_PHONE, True)
            text_out = u'Так не пойдет, нужно ввести ваш номер телефона в формате "код_страны код_оператора телефон". Пример: 7 495 1234567 %s' % Smile.SMILING_FACE_WITH_SMILING_EYE
            self.shop_telebot.send_message(message.chat.id, text_out)
        else:
            phone_number = message.text
            product_id = self.pseudo_session.get(CacheKey.PRODUCT_ID)
            product = Product.objects.get(id=product_id)
            buyer = Buyer.objects.filter(telegram_user_id=self.chat_id).get()
            buyer.phone = phone_number
            buyer.save()
            order = Order.objects.create(buyer=buyer, product=product)
            info_text = u'Заказ id=%s создан' % order.id
            logger.info(info_text)
            text_out = u'Спасибо, ваши контакты (%s) были отправлены менеджеру компании. Ожидайте он свяжется с вами' % phone_number
            self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)

            send_mail_to_the_shop(order)

    def handle_send_message_to_administator(self, message):
        self._core_question_to_bot_support(message)


    def handle_default(self, message):
        # дефолтный хэдлер, если не нашло подходящий
        text_out = u'Команда "%s" не найдена, попробуйте выбрать другую команду' % message.text
        self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)
        if not settings.DEBUG:
            logger.warning(u'Запрос не обработался: %s' % message)

    def handle_answer_from_bot_support(self, message):
        self._core_answer_from_bot_support(message)

    def handle_question_to_bot_support(self, message):
        self._core_question_to_bot_support(message)

    def handle_start_question_about_product(self, call):
        call_data = call.data
        query_dict = get_query_dict(call_data)
        product_id = int(query_dict.get('product_id'))
        text_out = u'Товар N. Задайте вопрос по товару N'

        self._start_question_dialog(product_id)

        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.close_product_dialog_markup)

    def handle_close_question_dialog(self, message):
        self._close_question_dialog()

    def _start_question_dialog(self, product_id=None):
        key_value = CacheKeyValue().QUESTION_MODE
        if product_id:
            key_value.data.update(product_id=product_id)
        self.pseudo_session.set(key_value.get_cache_key(), key_value.data)

    def _close_question_dialog(self):
        self.pseudo_session.delete(CacheKeyValue().QUESTION_MODE.get_cache_key())
        text_out = u'Разговор закончен. Спасибо.'
        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.menu_markup)

    def _core_question_to_bot_support(self, message):
        if not self.bot_support_chat_id:
            text_out = u'К сожалению к данному боту не подключен оператор поддержки клиентов ((.\n' \
                   u'Поэтому ваше сообщение оправлено администратору по email. Ответ в течение 1-48 часов'

            buyer = Buyer.objects.filter(telegram_user_id=message.chat.id).get()
            Feedback.objects.create(bot_id=self.bot_id, description=message.text, buyer=buyer)
            user_contacts = u'%s %s, %s' % (buyer.first_name, buyer.last_name, buyer.phone)
            mail_text = u'Сообщение: %s\n От кого: %s' % (message.text, user_contacts)

            # todo: вынести отправку письма в celery, добавить кнопку с телефоном, если он не заполнен
            result = send_mail(u'От бота артбелки', mail_text, settings.EMAIL_FULL_ADDRESS, [settings.EMAIL_SHOP_BOT_ADMIN])

            self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)
            logger.warning(u'Не установлен оператор поддержки для бота id=%s' % self.bot_id)

            self.pseudo_session.delete(CacheKeyValue().QUESTION_MODE.get_cache_key())

            return

        markup = types.ForceReply()
        text_out = u'Пользователь: %s %s (id=%s) Спрашивает:\n%s' % (message.chat.first_name, message.chat.last_name, message.chat.id, message.text)
        self.shop_telebot.send_message(self.bot_support_chat_id, text=text_out, reply_markup=markup)

        key_value = CacheKeyValue().QUESTION_MODE
        key_value_cached = self.pseudo_session.get(key_value.get_cache_key(), {})
        logger.info(self.chat_id)
        if not key_value_cached.get('is_buyer_notified'):
            self.shop_telebot.send_message(self.chat_id, text=u'*Bot*: Я передал сообщение администратору. Я передам все что напишите до нажатия на "Закончить разговор" ', parse_mode='markdown')
            key_value.data['is_buyer_notified'] = True
            self.pseudo_session.set(key_value.get_cache_key(), key_value.data)

    def _core_answer_from_bot_support(self, message):
        buyer_chat_id = re.search(TsdRegExp.FIND_USER_IN_REPLY, message.reply_to_message.text).group(1)

        # введем пользователя в режим диалога с администратором если этот режим был закрыт
        key_value = CacheKeyValue().QUESTION_MODE
        if not self.pseudo_session.get(key_value.get_cache_key(), chat_id=buyer_chat_id):
            key_value.data.update(is_buyer_notified=True)
            self.pseudo_session.set(key_value.get_cache_key(), key_value.data, chat_id=buyer_chat_id)

        text_out = u'*Администратор*: %s' % message.text
        self.shop_telebot.send_message(buyer_chat_id, text=text_out, reply_markup=self.close_product_dialog_markup, parse_mode='markdown')

    def _core_get_product_description(self):
        pass


