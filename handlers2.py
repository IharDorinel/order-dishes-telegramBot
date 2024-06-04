from telebot import types
import menu

def start_markup():
    """Creates and returns the main menu keyboard markup."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton('📋 Посмотреть меню'))
    markup.add(types.KeyboardButton('🛒 Корзина'))
    markup.add(types.KeyboardButton('🛍️ Посмотреть статус заказа'))
    return markup

def category_markup():
    """Creates and returns the inline keyboard markup with categories."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    categories = menu.categories()
    for emoji, name in categories:
        markup.add(types.KeyboardButton(f'{emoji} {name}'))
    markup.add(types.KeyboardButton('Назад в основное меню'))  # Добавляем кнопку "Назад в основное меню"
    return markup

def items_markup(category_name):
    """Creates and returns the inline keyboard markup with items for a given category."""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    items = menu.items_by_category(category_name)
    for item in items:
        markup.add(types.KeyboardButton(item))
    markup.add(types.KeyboardButton('Назад в категории'))
    return markup

def dish_markup():
    """Creates and returns the inline keyboard markup with options for a dish."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить в корзину', callback_data='add_to_cart'))
    markup.add(types.InlineKeyboardButton('Прочитать отзыв', callback_data='read_review'))
    return markup

def start_perform_actions(message, bot):
    msg = bot.send_message(
        message.chat.id,
        f'{message.from_user.first_name}! Выберите действие:',
        reply_markup=start_markup()
    )
    bot.register_next_step_handler(msg, handle_main_menu)

def handle_main_menu(message, bot):
    if message.text == '📋 Посмотреть меню':
        msg = bot.send_message(
            message.chat.id,
            f'{message.from_user.first_name}! Выберите нужную категорию.',
            reply_markup=category_markup()
        )
        bot.register_next_step_handler(msg, lambda m: category_selected(m, bot)
                                       )
        elif message.text.startswith('🛒 Корзина'):
        bot.send_message(message.chat.id, 'Функция корзина')
    elif message.text == '🛍️ Посмотреть статус заказа':
        bot.send_message(message.chat.id, 'Функция статус заказа')


def category_selected(message, bot):
    if message.text == 'Назад в основное меню':
        start_perform_actions(message, bot)
    else:
        category_name = message.text.split(' ', 1)[1]  # Извлекаем название категории из текста кнопки
        msg = bot.send_message(
            message.chat.id,
            f'Вы выбрали категорию: {category_name}. Выберите блюдо:',
            reply_markup=items_markup(category_name)
        )
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

