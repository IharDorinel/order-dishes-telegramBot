# Функции-обработчики для команд и нажатия кнопок
import telebot

from database import menu
from telebot import types
import feedback as fb

basket = 0
API_TOKEN = 'YOUR TOKEN'

bot = telebot.TeleBot(API_TOKEN)

def start_markup():
    """Creates and returns the initial reply keyboard markup for the bot."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add('\U0001F4CB Посмотреть меню', f'\U0001F6D2 Корзина ({str(basket)})',
               '\U0001F6F5 Посмотреть статус заказа')
    return markup


def feedback_markup():
    """Creates and returns the reply keyboard markup for feedback categories."""
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    markup.add('О сервисе ресторана', 'О блюдах')
    return markup


def start_message(message, bot):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте, {message.from_user.first_name}! Я чат-бот, который поможет тебе сделать заказ еды.',
                           reply_markup=start_markup())

    bot.register_next_step_handler(msg, lambda m: start_perform_actions(m, bot))


def feedback_message(message, bot):
    bot.send_message(
        message.chat.id,
        f'Здравствуйте, {message.from_user.first_name}! Оставьте, пожалуйста, отзыв о нашем сервисе, выбрав категорию ниже.',
        reply_markup=feedback_markup())
    bot.register_next_step_handler(message, lambda m: fb.choose_category(m, bot))


def support_message(message, bot):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте, {message.from_user.first_name}! Здесь вы можете обратиться за поддержкой.')


def category_markup():
    """Creates and returns the inline keyboard markup with categories."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    categories = menu.categories()
    for emoji, name in categories:
        markup.add(types.KeyboardButton(f'{emoji} {name}'))
    markup.add(types.KeyboardButton('Назад в основное меню'))  # Добавляем кнопку "Назад в основное меню"
    return markup


def items_markup(category_name):
    """Creates and returns the reply keyboard markup with items for the given category."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
    # Загружаем список блюд из выбранной категории
    items_list = menu.items_by_category(category_name)  # Предполагается, что такая функция существует в menu
    # Создаем кнопки
    buttons = [f"{item_name}" for item_name in items_list]
    button1 = types.KeyboardButton('Назад в категории')
    markup.add(*buttons)
    markup.add(button1)
    return markup


def dish_markup(dish_id):
    print('dish_id', dish_id)
    """Creates and returns the inline keyboard markup with options for a dish."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить в корзину', callback_data=f'add_to_cart:{dish_id}'))
    markup.add(types.InlineKeyboardButton('Прочитать отзыв', callback_data='read_review'))
    return markup

# Обработчик callback данных
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart'))
def handle_callback(call):
    print(call.data)
    dish_id = call.data.split(':')[1]
    add_to_order(call.message, dish_id)

# Обработчик добавления блюда в заказ
def add_to_order(message, dish_id):
    bot.send_message(message.chat.id, "Введите количество:")
    bot.register_next_step_handler(message, lambda m: process_amount(m, dish_id))

def process_amount(message, dish_id):
    try:
        amount = int(message.text)
        bot.send_message(message.chat.id, f"Блюдо {dish_id} добавлено в корзину в количестве {amount}!")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное количество.")

def start_perform_actions(message, bot):
    if message.text == '📋 Посмотреть меню':
        msg = bot.send_message(
            message.chat.id,
            f'{message.from_user.first_name}! Выберите нужную категорию.',
            reply_markup=category_markup()
        )
        bot.register_next_step_handler(msg, lambda m: category_selected(m, bot))
    elif message.text.startswith('🛒 Корзина'):
        bot.send_message(message.chat.id, 'Функция корзина')
    elif message.text == '\U0001F6F5 Посмотреть статус заказа':
        bot.send_message(message.chat.id, 'Функция статус заказа')


def category_selected(message, bot):
    if message.text == 'Назад в основное меню':
        msg = bot.send_message(
            message.chat.id,
            reply_markup=start_message(message, bot)
        )
    else:
        category_name = message.text.split(' ', 1)[1]  # Извлекаем название категории из текста кнопки
        msg = bot.send_message(
            message.chat.id,
            f'Вы выбрали категорию: {category_name}. Выберите блюдо:',
            reply_markup=items_markup(category_name)
        )
        # Здесь можно зарегистрировать следующий шаг, если требуется дополнительная обработка
        bot.register_next_step_handler(msg, lambda m: dish_selected(m, bot))


def dish_selected(message, bot):
    if message.text == 'Назад в категории':
        msg = bot.send_message(
            message.chat.id,
            f'{message.from_user.first_name}! Выберите нужную категорию.',
            reply_markup=category_markup()
        )
        bot.register_next_step_handler(msg, lambda m: category_selected(m, bot))

    else:

        dish_name = message.text
        details = menu.dish_details(dish_name)

        if details:
            dish_id, description, price, image_url = details
            caption = f"{dish_name}\n\n{description}\n\nЦена: {price} руб."
            with open(image_url, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=dish_markup(dish_id)
                )
        bot.register_next_step_handler(message, lambda m: dish_selected(m, bot))
