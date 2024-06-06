import telebot
import feedback as fb
import handlers


bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')


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
    fb.dish_category(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dish:'))
def choose_dish(call):
    fb.fb_dish_selected(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back:'))
def back_to_category(call):
    fb.choose_category(call.message, bot)

bot.polling(none_stop=True)
