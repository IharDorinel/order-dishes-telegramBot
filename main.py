import telebot

import handlers



bot = telebot.TeleBot('YOUR_TOKEN_HERE')


@bot.message_handler(commands=['start'])
def start_message(message):
    handlers.start_message(message, bot)


@bot.message_handler(commands=['feedback'])
def start_message(message):
    handlers.feedback_message(message, bot)


@bot.message_handler(commands=['support'])
def start_message(message):
    handlers.support_message(message, bot)


bot.polling(none_stop=True)
