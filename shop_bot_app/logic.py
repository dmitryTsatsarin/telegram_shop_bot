# -*- coding: utf-8 -*-
import logging

import telebot
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.mail import send_mail
from telebot import types

from shop_bot_app.models import Product, Customer, Order, Feedback

logger = logging.getLogger(__name__)
to_log = logger.info


bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)

menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_markup.row(u'Каталог', u'Распродажа %')
menu_markup.row(u'FAQ (Помощь)', u'Задать вопрос')

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
def handle_faq(message):
    text_out = u'Вопрос 1\n Ответ1'
    bot.send_message(message.chat.id, text_out)

    text_out = u'Вопрос 2\n Ответ2'
    bot.send_message(message.chat.id, text_out)

    text_out = u'Вопрос 3\n Ответ3'
    bot.send_message(message.chat.id, text_out)


@bot.message_handler(func=lambda message: message.text.lower().startswith(u'каталог'), content_types=['text'])
def handle_catalog(message):
    queryset = Product.objects.order_by('-id')[:10]
    all_products = list(queryset)
    for product in all_products:
        image_file = ImageFile(product.picture)
        order_command = u'/get_it_%s' % product.id
        caption = u'Наименование: %s\nОписание: %s\nЦена: %s' % (product.name, product.description, product.price)

        markup = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
        markup.add(callback_button)

        bot.send_photo(message.chat.id, image_file, caption=caption, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.lower().startswith(u'распродажа'), content_types=['text'])
def handle_catalog_discount(message):
    queryset = Product.objects.filter(is_discount=True).order_by('-id')[:10]
    products = list(queryset)

    for product in products:
        image_file = ImageFile(product.picture)
        order_command = u'/get_it_%s' % product.id
        caption = u'Наименование: %s\nОписание: %s\nЦена: %s\nТОРОПИТЕСЬ ТОВАР НА СКИДКЕ' % (product.name, product.description, product.price)

        markup = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
        markup.add(callback_button)

        bot.send_photo(message.chat.id, image_file, caption=caption, reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone_number = message.contact.phone_number
    customer = Customer.objects.filter(chat_id=message.chat.id).get()
    customer.phone = phone_number
    customer.save()
    text_out = u'Спасибо, ваши контакты (%s) были отправлены менеджеру компании. Ожидайте он свяжется с вами' % phone_number
    bot.send_message(message.chat.id, text_out, reply_markup=menu_markup)


@bot.callback_query_handler(func=lambda call: call.data.lower().startswith(u'/get_it_'))
def callback_catalog_order(call):

    customer = Customer.objects.filter(chat_id=call.message.chat.id).get()
    product_id = int(call.data.lower().replace(u'/get_it_', ''))
    product = Product.objects.filter(id=product_id).get()
    Order.objects.create(customer=customer, product=product)

    markup = types.ReplyKeyboardMarkup(row_width=1)
    phone_btn = types.KeyboardButton(u'отправить номер телефона', request_contact=True)
    markup.add(phone_btn)
    text_out = u'*Заказ оформлен* (%s).\n\n Укажите ваш номер телефона и менеджер вам перезвонит' % product.name
    bot.send_message(call.message.chat.id, text_out, reply_markup=markup, parse_mode='markdown')


@bot.message_handler(func=lambda message: message.text.lower().startswith(u'задать вопрос'), content_types=['text'])
def handle_send_message_to_administator_preview(message):
    text_out = u'Задайте вопрос администратору:'

    markup = types.ForceReply()
    bot.send_message(message.chat.id, text_out, reply_markup=markup)


def if_func(message):
    return message.reply_to_message and message.reply_to_message.text.lower().startswith(u'задайте вопрос администратору')

@bot.message_handler(func=if_func, content_types=['text'])
def handle_send_message_to_administator(message):
    customer = Customer.objects.filter(chat_id=message.chat.id).get()
    Feedback.objects.create(description=message.text, customer=customer)
    user_contacts =u'%s %s, %s' % (customer.first_name, customer.last_name, customer.phone)
    mail_text = u'Сообщение: %s\n От кого: %s' % (message.text, user_contacts)

    send_mail('От бота артбелки', mail_text, settings.EMAIL_FULL_ADDRESS, [settings.EMAIL_BOT_ADMIN])
    text_out = u'Ваше сообщение оправлено администратору. Ответ в течение 1-48 часов'
    bot.send_message(message.chat.id, text_out, reply_markup=menu_markup)


@bot.message_handler(content_types=['text'])
def handle_default(message):
    # дефолтный хэдлер, если не нашло подходящий
    text_out = u'Команда "%s" не найдена, попробуйте выбрать другую команду' % message.text
    bot.send_message(message.chat.id, text_out, reply_markup=menu_markup)
    logger.error(u'Запрос не обработался: %s' % message)




