# Функции-обработчики для команд и нажатия кнопок
import telebot
import requests
from database import menu
from database.order import *
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
    markup.add(types.InlineKeyboardButton('Добавить в корзину', callback_data=f"add_to_cart:{dish_id}"))
    markup.add(types.InlineKeyboardButton('Прочитать отзыв', callback_data='read_review'))
    return markup


def start_perform_actions(message, bot):
    if message.text == '📋 Посмотреть меню':
        msg = bot.send_message(
            message.chat.id,
            f'{message.from_user.first_name}! Выберите нужную категорию.',
            reply_markup=category_markup()
        )
        bot.register_next_step_handler(msg, lambda m: category_selected(m, bot))
    elif message.text.startswith('🛒 Корзина'):
        #bot.send_message(message.chat.id, 'Функция корзина')
        display_order(message, bot)
        bot.register_next_step_handler(message, lambda m: start_perform_actions(m, bot))
    elif message.text == '\U0001F6F5 Посмотреть статус заказа':
        bot.send_message(message.chat.id, 'Функция статус заказа')


def category_selected(message, bot):
    if message.text == 'Назад в основное меню':
        msg = bot.send_message(
            message.chat.id, 'Выберите дальнейшее действие:',
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


def add_to_order(message, dish_id, order, bot):
    for position in order.positions:
        if position.dish_id == dish_id:
            bot.send_message(message.chat.id, "Блюдо уже есть в заказе. Вы можете отредактировать количество в корзине.")
            return
    bot.send_message(message.chat.id, "Введите количество:")
    bot.register_next_step_handler(message, lambda m: process_amount(m, dish_id, order, bot))

def process_amount(message, dish_id, order, bot):
    db = Database('EasyEats.db')
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError("Количество должно быть больше нуля.")
        #menu_item = db.cursor.execute("SELECT price FROM menu WHERE dish_id = ?", (dish_id,)).fetchone()
        menu_item = db.get_dish(dish_id)
        if menu_item:
            price = menu_item[4]
            #name = menu_item[2]
            #db.add_order_position(order.order_id, dish_id, price, amount)
            position = Position(dish_id, amount, price)
            order.add_position(position)
            bot.send_message(message.chat.id, "Блюдо добавлено в заказ.")
            #####
            show_order(message, bot, order)
            #####
        else:
            bot.send_message(message.chat.id, "Блюдо не найдено.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное количество.")


def order_markup(order):
    """Creates and returns the inline keyboard markup with options for a cart."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Удалить позицию', callback_data="delete_position"))
    markup.add(types.InlineKeyboardButton('Изменить количество в позиции', callback_data="change_position"))
    markup.add(types.InlineKeyboardButton('Очистить корзину', callback_data='clear_cart'))
    markup.add(types.InlineKeyboardButton('Оформить заказ', callback_data='checkout'))
    return markup


# Обработчик команды /order для просмотра текущего заказа
#@bot.message_handler(commands=['order'])
def show_order(message, bot, order):
    db = Database('EasyEats.db')
    # user_id = message.from_user.id
    # order = user_data[user_id]['order']
    #order_items = db.get_order(order.order_id)
    # if not order_items:
    #     bot.send_message(message.chat.id, "Ваш заказ пуст.")
    # else:
    #     order_details = ""
    #     total_price = 0
    #     for item in order_items:
    #         dish_name, amount, price, item_total_price = item
    #         order_details += f"{dish_name} x{amount} - {price} руб. за шт. (Итого: {item_total_price} руб.)\n"
    #         total_price += item_total_price
    #     order_details += f"\nОбщая сумма заказа: {total_price} руб."
    #     bot.send_message(message.chat.id, order_details)
    if not order.positions:
        bot.send_message(message.chat.id, "Ваш заказ пуст.")
    else:
        order_details = ""
        ind = 0
        for item in order.positions:
            menu_item = db.get_dish(item.dish_id)
            dish_name = menu_item[2]
            ind += 1
            # dish_name = db.cursor.execute("SELECT dish_name FROM menu WHERE dish_id = ?", (dish_id,)).fetchone()
            order_details += f"{ind}. {dish_name} x{item.amount} - {item.price} руб. за шт. (Итого: {item.total_price} руб.)\n"
        order_details += f"\nОбщая сумма заказа: {order.total_price} руб."
        bot.send_message(message.chat.id, order_details, reply_markup=order_markup(order))
    db.close()


# Обработчик команды /delete для удаления позиции из заказа
#@bot.message_handler(commands=['delete'])
# @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_position:'))
# def delete_from_order(call):
#     order = call.data.split(':')[1]
#     bot.send_message(call.message.chat.id, "Введите № позиции для удаления:")
#     bot.register_next_step_handler(call.message, process_delete)


def process_delete(message, bot, order):
    try:
        pos_id = int(message.text)
        # user_id = message.from_user.id
        # order = user_data[user_id]['order']
        pos_for_delete = order.positions[pos_id-1]
        order.remove_position(pos_for_delete)
        #db.delete_order_position(pos_id)
        bot.send_message(message.chat.id, "Позиция удалена из заказа.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный № позиции.")

    # Обработчик команды /confirm для подтверждения заказа
    @bot.message_handler(commands=['confirm'])
    def confirm_order(message):
        bot.send_message(message.chat.id, "Ваш заказ подтвержден. Спасибо за покупку!")

def process_change(message, bot, order):
    try:
        pos_id = int(message.text)
        pos_for_change = order.positions[pos_id-1]
        bot.send_message(message.chat.id, "Введите количество:")
        bot.register_next_step_handler(message, lambda m: process_change_amount(m, bot, order, pos_for_change))

    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный № позиции.")

def process_change_amount(message, bot, order, position):
    db = Database('EasyEats.db')
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError("Количество должно быть больше нуля.")
        else:
            position.change_amount(amount)
            order.recalculate_total_price()
            bot.send_message(message.chat.id, "Позиция изменена.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное количество.")


#@bot.message_handler(commands=['order'])
def display_order(message, bot):
    user_id = message.from_user.id
    order = user_data[user_id]['order']
    show_order(message, bot, order)