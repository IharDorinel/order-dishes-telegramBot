from telebot import types
from database import menu  # Предполагается, что у вас есть модуль menu для работы с меню



basket = 0

def start_markup():
    """Creates and returns the initial reply keyboard markup for the bot."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add('\U0001F4CB Посмотреть меню', f'\U0001F6D2 Корзина ({str(basket)})',
               '\U0001F6F5 Посмотреть статус заказа', 'Ввести адрес доставки')
    return markup


def start_message(message, bot):
    msg = bot.send_message(message.chat.id,
                           f'Здравствуйте, {message.from_user.first_name}! Я чат-бот, который поможет тебе сделать заказ еды.',
                           reply_markup=start_markup())

    bot.register_next_step_handler(msg, lambda m: start_perform_actions(m, bot))


def feedback_message(message, bot):
    bot.send_message(message.chat.id,
                     f'Здравствуйте, {message.from_user.first_name}! Оставьте, пожалуйста, отзыв о нашем сервисе.')


def support_message(message, bot):
    bot.send_message(message.chat.id,
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


def dish_markup():
    """Creates and returns the inline keyboard markup with options for a dish."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить в корзину', callback_data='add_to_cart'))
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
        bot.send_message(message.chat.id, 'Функция корзина')
    elif message.text == '\U0001F6F5 Посмотреть статус заказа':
        bot.send_message(message.chat.id, 'Функция статус заказа')
    elif message.text == 'Ввести адрес доставки':
        request_address(message, bot)


def category_selected(message, bot):
    if message.text == 'Назад в основное меню':
        start_message(message, bot)
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
            description, price, image_url = details
            caption = f"{dish_name}\n\n{description}\n\nЦена: {price} руб."
            with open(image_url, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=dish_markup()
                )
        bot.register_next_step_handler(message, lambda m: dish_selected(m, bot))


def address_markup():
    """Creates and returns the inline keyboard markup for entering the delivery address."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton('Введите адрес доставки'))
    return markup


def request_address(message, bot):
    """Function to request delivery address from the user."""
    msg = bot.send_message(message.chat.id, "Пожалуйста, введите свой адрес доставки заказа:", reply_markup=address_markup())
    bot.register_next_step_handler(msg, lambda m: save_address(m, bot))


def save_address(message, bot):
    """Function to save user's delivery address."""
    user_id = message.from_user.id
    address = message.text
    # В этой функции вы можете сохранить адрес пользователя в базе данных или как-то еще его обработать
    bot.send_message(message.chat.id, f"Адрес доставки сохранен: {address}")

    # Создаем кнопку "Возврат в основное меню"
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_main_menu = types.KeyboardButton('Возврат в основное меню')
    markup.add(btn_main_menu)

    bot.send_message(message.chat.id, "Вы можете вернуться в основное меню", reply_markup=markup)


    # Установите ваш секретный ключ Stripe


