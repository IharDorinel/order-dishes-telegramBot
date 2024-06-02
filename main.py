import telebot



bot = telebot.TeleBot('insert your token')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, 'Привет! Я чат-бот,который поможет тебе сделать заказ еды.')



bot.polling(none_stop=True)