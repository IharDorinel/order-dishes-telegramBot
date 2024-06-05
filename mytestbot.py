import telebot
from telebot import types
import handlers

# Используем ваш реальный API токен
bot = telebot.TeleBot('6780123582:AAEyvSQofZcMq2FUnMQNdUQUgUBFMxSzlQ8')

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


# Запуск бота
bot.polling(none_stop=True)
