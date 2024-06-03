# Функции-обработчики для команд и нажатия кнопок

from telebot import types

basket = 0

def start_markup():
    """Creates and returns the initial reply keyboard markup for the bot."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add('\U0001F4CB Посмотреть меню', f'\U0001F6D2 Корзина ({str(basket)})',
               '\U0001F6F5 Посмотреть статус заказа')
    return markup

def start_message(message, bot):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте, {message.from_user.first_name}! Я чат-бот, который поможет тебе сделать заказ еды.',
                           reply_markup=start_markup())

def feedback_message(message, bot):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте, {message.from_user.first_name}! Оставьте, пожалуйста, отзыв о нашем сервисе.')


def support_message(message, bot):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте, {message.from_user.first_name}! Здесь вы можете обратиться за поддержкой.')