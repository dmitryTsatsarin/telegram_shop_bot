# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.mail import send_mail
from telebot import types

from shop_bot_app.helpers import TextCommandEnum, send_mail_to_the_shop
from shop_bot_app.models import Product, Buyer, Order, Feedback, Bot, Catalog, BotBuyerMap
from shop_bot_app.utils import create_shop_telebot

logger = logging.getLogger(__name__)
to_log = logger.info


def send_schedule_product(telegram_user_id, product_id, text_before):
    product = Product.objects.filter(id=product_id).get()

    image_file = ImageFile(product.picture)
    order_command = u'/get_it_%s' % product.id
    caption = u'%s\nНаименование: %s\nОписание: %s\nЦена: %s' % (text_before, product.name, product.description, product.price)

    markup = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
    markup.add(callback_button)
    shop_telebot = create_shop_telebot(product.bot.telegram_token)
    shop_telebot.send_photo(telegram_user_id, image_file, caption=caption, reply_markup=markup)


def initialize_bot_with_routing(token, session):
    shop_telebot = create_shop_telebot(token)
    bot_id = Bot.objects.get(telegram_token=token).id

    menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_markup.row(u'Каталог', u'Распродажа %')
    menu_markup.row(u'FAQ (Помощь)', u'Задать вопрос')

    # Обработчик команд '/start'
    @shop_telebot.message_handler(commands=['start',])
    def handle_start_help(message):
        telegram_user_id = message.chat.id
        # create buyer
        try:
            BotBuyerMap.objects.filter(buyer__telegram_user_id=telegram_user_id, bot__telegram_token=token).get()
        except BotBuyerMap.DoesNotExist as e:
            first_name = message.chat.first_name
            last_name = message.chat.last_name
            buyer, _ = Buyer.objects.get_or_create(telegram_user_id=telegram_user_id, defaults=dict(
                        first_name=first_name,
                        last_name=last_name,
                        telegram_user_id=telegram_user_id
                )
            )
            bot = Bot.objects.filter(telegram_token=token).get()
            BotBuyerMap.objects.create(bot=bot, buyer=buyer)

        text_out = 'Привет! Я бот магазина одежды "АртБелкаДемоБот". Я могу принимать твои заказы и сообщать о скидках и акциях!'
        shop_telebot.send_message(message.chat.id, text_out)

        # markup = types.ReplyKeyboardMarkup()
        # markup.row('Каталог', 'Распродажа %')
        # markup.row('Заказы', 'Корзина')
        # markup.row('Настройки', 'Помощь')
        shop_telebot.send_message(message.chat.id, "Сделайте ваш выбор:", reply_markup=menu_markup)


    @shop_telebot.message_handler(func=lambda message: message.text.lower().startswith(u'faq'), content_types=['text'])
    def handle_faq(message):
        text_out = u'Наши контакты\n +711111111111'
        shop_telebot.send_message(message.chat.id, text_out)

        text_out = u'Вопрос 1\n Ответ1'
        shop_telebot.send_message(message.chat.id, text_out)

        text_out = u'Вопрос 2\n Ответ2'
        shop_telebot.send_message(message.chat.id, text_out)

        text_out = u'Вопрос 3\n Ответ3'
        shop_telebot.send_message(message.chat.id, text_out)


    @shop_telebot.message_handler(func=lambda message: message.text.lower().startswith(u'каталог'), content_types=['text'])
    def handle_catalog(message):
        catalogs = list(Catalog.objects.filter(bot_id=bot_id))
        markup = types.InlineKeyboardMarkup()
        for catalog in catalogs:
            order_command = u'/get_catalog_%s' % catalog.id
            products_count = Product.objects.filter(catalog_id=catalog.id, bot_id=bot_id).count()
            text = u'%s (%s)' % (catalog.name, products_count)
            callback_button = types.InlineKeyboardButton(text=text, callback_data=order_command)
            markup.add(callback_button)
        shop_telebot.send_message(message.chat.id, 'Каталоги', reply_markup=markup)

    @shop_telebot.callback_query_handler(func=lambda call: call.data.lower().startswith(TextCommandEnum.GET_CATALOG))
    def handle_show_catalog_products(call):
        catalog_id = int(call.data.lower().replace(TextCommandEnum.GET_CATALOG, ''))

        queryset = Product.objects.filter(bot_id=bot_id, catalog_id=catalog_id).order_by('-id')[:10]
        all_products = list(queryset)
        # todo: возможно стоит вынести общую часть в отдельные функции
        for product in all_products:
            image_file = ImageFile(product.picture)
            order_command = u'%s%s' % (TextCommandEnum.GET_PRODUCT, product.id)
            caption = u'Наименование: %s\nОписание: %s\nЦена: %s' % (product.name, product.description, product.price)

            markup = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
            markup.add(callback_button)
            shop_telebot.send_photo(call.message.chat.id, image_file, caption=caption, reply_markup=markup)
        if not all_products:
            shop_telebot.send_message(call.message.chat.id, u'Каталог пуст')


    @shop_telebot.message_handler(func=lambda message: message.text.lower().startswith(u'распродажа'), content_types=['text'])
    def handle_catalog_discount(message):
        queryset = Product.objects.filter(bot_id=bot_id, is_discount=True).order_by('-id')[:10]
        products = list(queryset)

        for product in products:
            image_file = ImageFile(product.picture)
            order_command = u'/get_it_%s' % product.id
            caption = u'Наименование: %s\nОписание: %s\nЦена: %s\nТОРОПИТЕСЬ ТОВАР НА СКИДКЕ' % (product.name, product.description, product.price)

            markup = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
            markup.add(callback_button)

            shop_telebot.send_photo(message.chat.id, image_file, caption=caption, reply_markup=markup)
        if not products:
            shop_telebot.send_message(message.chat.id, u'Нет товара на скидке')


    @shop_telebot.message_handler(content_types=['contact'])
    def handle_contact(message):
        phone_number = message.contact.phone_number
        buyer = Buyer.objects.filter(telegram_user_id=message.chat.id).get()
        buyer.phone = phone_number
        buyer.save()
        text_out = u'Спасибо, ваши контакты (%s) были отправлены менеджеру компании. Ожидайте он свяжется с вами' % phone_number
        shop_telebot.send_message(message.chat.id, text_out, reply_markup=menu_markup)
        text = u'Создан заказ %s' % session.get('order')
        send_mail_to_the_shop(text)


    @shop_telebot.callback_query_handler(func=lambda call: call.data.lower().startswith(u'/get_it_'))
    def callback_catalog_order(call):
        logger.debug('Оформление заказа')
        buyer = Buyer.objects.filter(telegram_user_id=call.message.chat.id).get()
        product_id = int(call.data.lower().replace(u'/get_it_', ''))
        product = Product.objects.filter(id=product_id).get()
        order = Order.objects.create(buyer=buyer, product=product)
        info_text = u'Заказ id=%s создан' % order.id
        logger.info(info_text)
        session['order'] = order.id

        markup = types.ReplyKeyboardMarkup(row_width=1)
        phone_btn = types.KeyboardButton(u'отправить номер телефона', request_contact=True)
        markup.add(phone_btn)
        text_out = u'*Заказ оформлен* (%s).\n\n Укажите ваш номер телефона и менеджер вам перезвонит' % product.name
        shop_telebot.send_message(call.message.chat.id, text_out, reply_markup=markup, parse_mode='markdown')


    @shop_telebot.message_handler(func=lambda message: message.text.lower().startswith(u'задать вопрос'), content_types=['text'])
    def handle_send_message_to_administator_preview(message):
        text_out = u'Задайте вопрос администратору:'

        markup = types.ForceReply()
        shop_telebot.send_message(message.chat.id, text_out, reply_markup=markup)


    def if_func(message):
        return message.reply_to_message and message.reply_to_message.text.lower().startswith(u'задайте вопрос администратору')

    @shop_telebot.message_handler(func=if_func, content_types=['text'])
    def handle_send_message_to_administator(message):
        buyer = Buyer.objects.filter(telegram_user_id=message.chat.id).get()
        Feedback.objects.create(bot_id=bot_id, description=message.text, buyer=buyer)
        user_contacts =u'%s %s, %s' % (buyer.first_name, buyer.last_name, buyer.phone)
        mail_text = u'Сообщение: %s\n От кого: %s' % (message.text, user_contacts)

        # todo: вынести отправку письма в celery, добавить кнопку с телефоном, если он не заполнен
        send_mail(u'От бота артбелки', mail_text, settings.EMAIL_FULL_ADDRESS, [settings.EMAIL_BOT_ADMIN])
        text_out = u'Ваше сообщение оправлено администратору. Ответ в течение 1-48 часов'
        shop_telebot.send_message(message.chat.id, text_out, reply_markup=menu_markup)


    @shop_telebot.message_handler(content_types=['text'])
    def handle_default(message):
        # дефолтный хэдлер, если не нашло подходящий
        text_out = u'Команда "%s" не найдена, попробуйте выбрать другую команду' % message.text
        shop_telebot.send_message(message.chat.id, text_out, reply_markup=menu_markup)
        logger.warning(u'Запрос не обработался: %s' % message)

    return shop_telebot




