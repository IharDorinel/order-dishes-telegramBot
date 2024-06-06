import telebot
import feedback as fb
import handlers
from database import order


bot = telebot.TeleBot('7367715020:AAEZortk_qDiDFA28I7LfAYnnbLsX1loE48')


commands = [
    telebot.types.BotCommand('/start', 'Запустить бота'),
    telebot.types.BotCommand('/feedback', 'Оставить отзыв'),
    telebot.types.BotCommand('/support', 'Обратиться в поддержку')
]

bot.set_my_commands(commands)


@bot.message_handler(commands=['start'])
def start_message(message):
    handlers.start_message(message, bot)


@bot.message_handler(commands=['feedback'])
def start_message(message):
    handlers.feedback_message(message, bot)


@bot.message_handler(commands=['support'])
def start_message(message):
    handlers.support_message(message, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('category:'))
def choose_dish_category(call):
    print('call', call.data)
    fb.dish_category(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dish:'))
def choose_dish(call):
    print('call', call.data)
    fb.fb_dish_selected(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart'))
def handle_callback(call):
    print(call.data)
    dish_id = call.data.split(':')[1]
    print('name', dish_id)
    handlers.add_to_order(call.message, dish_id)

bot.polling(none_stop=True)
