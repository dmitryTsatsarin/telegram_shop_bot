# -*- coding: utf-8 -*-
from shop_bot_app.models import Product, Customer, Order

from django.core.files.images import ImageFile
import logging

import telebot

from telebot import types

from django.conf import settings

logger = logging.getLogger(__name__)
to_log = logger.info


bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

def tsd_keys_handler(message, key):
    return message.text.lower().startswith(key)


menu_markup = types.ReplyKeyboardMarkup()
menu_markup.row(u'Каталог', u'Распродажа %')
menu_markup.row(u'FAQ (Помощь)', u'Написать администратору')

# Обработчик команд '/start'
@bot.message_handler(commands=['start',])
def handle_start_help(message):
    chat_id = message.chat.id
    # create customer
    try:
        customer = Customer.objects.filter(chat_id=chat_id).get()
    except Customer.DoesNotExist as e:
        first_name = message.chat.first_name
        last_name = message.chat.last_name
        customer = Customer.objects.create(chat_id=chat_id, first_name=first_name, last_name=last_name)

    text_out = 'Привет! Я бот магазина одежды "АртБелкаДемоБот". Я могу принимать твои заказы и сообщать о скидках и акциях!'
    bot.send_message(message.chat.id, text_out)

    # markup = types.ReplyKeyboardMarkup()
    # markup.row('Каталог', 'Распродажа %')
    # markup.row('Заказы', 'Корзина')
    # markup.row('Настройки', 'Помощь')
    bot.send_message(message.chat.id, "Сделайте ваш выбор:", reply_markup=menu_markup)


@bot.message_handler(func=lambda message: message.text.lower().startswith(u'faq'), content_types=['text'])
def handle_faq():
    pass


@bot.message_handler(func=lambda message: message.text.lower().startswith(u'каталог'), content_types=['text'])
def handle_catalog(message):
    queryset = Product.objects.order_by('-id')[:10]
    all_products = list(queryset)
    for product in all_products:
        image_file = ImageFile(product.picture)
        order_command = u'/get_it_%s' % product.id
        caption = u'Наименование: %s\nОписание: %s\nЦена: %s\nЗаказать: %s' % (product.name, product.description, product.price, order_command)
        bot.send_photo(message.chat.id, image_file, caption=caption)


@bot.message_handler(func=lambda message: message.text.lower().startswith(u'распродажа'), content_types=['text'])
def handle_catalog(message):
    queryset = Product.objects.filter(is_discount=True).order_by('-id')[:10]
    products = list(queryset)

    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Нажми меня", callback_data="test")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Я – сообщение из обычного режима", reply_markup=keyboard)
    for product in products:
        image_file = ImageFile(product.picture)
        order_command = u'/get_it_%s' % product.id
        caption = u'Наименование: %s\nОписание: %s\nЦена: %s\nЗаказать: %s\nТОРОПИТЕСЬ ТОВАР НА СКИДКЕ' % (product.name, product.description, product.price, order_command)
        bot.send_photo(message.chat.id, image_file, caption=caption)


@bot.message_handler(func=lambda message: message.text.lower().startswith(u'/get_it_'), content_types=['text'])
def handle_order(message):
    text_out = u'Укажите ваш номер телефона и менеджер вам перезвонит'

    customer = Customer.objects.filter(chat_id=message.chat.id).get()
    product_id = int(message.text.lower().replace(u'/get_it_',''))
    product = Product.objects.filter(id=product_id).get()
    Order.objects.create(customer=customer, product=product)

    markup = types.ReplyKeyboardMarkup(row_width=1)
    phone_btn = types.KeyboardButton(u'отправить номер телефона', request_contact=True)
    markup.add(phone_btn)
    bot.send_message(message.chat.id, text_out, reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone_number = message.contact.phone_number
    customer = Customer.objects.filter(chat_id=message.chat.id).get()
    customer.phone = phone_number
    customer.save()
    text_out = u'Спасибо, ваши контакты (%s) были отправлены менеджеру компании. Ожидайте он свяжется с вами' % phone_number
    bot.send_message(message.chat.id, text_out, reply_markup=menu_markup)


# @bot.message_handler(content_types=['text'])
# def handle_faq(message):
#     pass




