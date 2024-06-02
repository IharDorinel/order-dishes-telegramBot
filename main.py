import telebot
from telebot import types

basket = 0


def start_markup():
    """Creates and returns the initial reply keyboard markup for the bot."""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    markup.add('\U0001F4CB Посмотреть меню', f'\U0001F6D2 Корзина ({str(basket)})',
               '\U0001F6F5 Посмотреть статус заказа')
    return markup


bot = telebot.TeleBot('YOUR_TOKEN_HERE')


@bot.message_handler(commands=['start'])
def start_message(message):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте! {message.from_user.first_name}, Я чат-бот,который поможет тебе сделать заказ еды.',
                           reply_markup=start_markup())


@bot.message_handler(commands=['feedback'])
def start_message(message):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте! {message.from_user.first_name}, У нас лучший в городе Ресторан.')


@bot.message_handler(commands=['support'])
def start_message(message):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте! {message.from_user.first_name}, Помоги себе сам.')


bot.polling(none_stop=True)
