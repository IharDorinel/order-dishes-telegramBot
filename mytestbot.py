import telebot

from telebot import types
from oplata_zakaza import process_payment  # Импортируем функцию оплаты из файла oplata_zakaza.py

import handlers

# Используем ваш реальный API токен
bot = telebot.TeleBot('')

commands = [
    telebot.types.BotCommand('/start', 'Запустить бота'),
    telebot.types.BotCommand('/feedback', 'Оставить отзыв'),
    telebot.types.BotCommand('/support', 'Обратиться в поддержку')
]

bot.set_my_commands(commands)

# Словарь для хранения адресов доставки пользователей
user_addresses = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    handlers.start_message(message, bot)


@bot.message_handler(commands=['feedback'])
def feedback_message(message):
    handlers.feedback_message(message, bot)


@bot.message_handler(commands=['support'])
def support_message(message):
    handlers.support_message(message, bot)


@bot.message_handler(func=lambda message: message.text == 'Ввести адрес доставки')
def request_address(message):
    handlers.request_address(message, bot)


@bot.message_handler(func=lambda message: message.text == 'Оплата заказа')
def handle_payment_button(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add('Наличными', 'Банковской картой')
    bot.send_message(message.chat.id, "Выберите способ оплаты:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Наличными')
def handle_cash_payment(message):
    bot.send_message(message.chat.id, "Оплатите наличными курьеру в момент доставки")

@bot.message_handler(func=lambda message: message.text == 'Банковской картой')
def handle_card_payment(message):
    bot.send_message(message.chat.id, "Оплата прошла успешно")

# @bot.message_handler(func=lambda message: message.text == 'Оплата заказа')
# def handle_payment_button(message):
#     handle_payment(message)
#
#
# @bot.message_handler(commands=['pay'])
# def handle_payment(message):
#     # Пример данных для оплаты (в реальном приложении эти данные нужно получить от пользователя безопасным способом)
#     user_id = message.from_user.id
#     order_id = 12345  # Это должен быть реальный ID заказа из базы данных
#     card_number = '4242424242424242'
#     exp_month = 12
#     exp_year = 2024
#     cvc = '123'
#     amount = 1000  # 1000 копеек = 10 рублей
#
#     # Вызов функции оплаты
#     result = process_payment(user_id, order_id, card_number, exp_month, exp_year, cvc, amount)
#
#     # Обработка результата оплаты
#     if result['status'] == 'success':
#        bot.send_message(message.chat.id, f"Оплата успешна! Идентификатор платежа: {result['charge_id']}")
#     else:
#        bot.send_message(message.chat.id, f"Ошибка при оплате: {result['message']}")
@bot.message_handler(func=lambda message: message.text == 'Возврат в основное меню')
def return_to_main_menu(message):
    handlers.start_message(message, bot)

# Запуск бота
bot.polling(none_stop=True)

