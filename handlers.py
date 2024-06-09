# Функции-обработчики для команд и нажатия кнопок
import telebot
from database import menu, user
from database.order import *
from telebot import types
import feedback as fb


# Глобальная переменная для хранения количества товаров в корзине
basket = 0


def start_message(message, bot):
    """
    Отправляет приветственное сообщение пользователю и предлагает выбрать дальнейшее действие.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    msg = bot.send_message(
        message.chat.id,
        f'Здравствуйте, {message.from_user.first_name}! Я бот, который поможет тебе выбрать и '
        f'заказать лучшие блюда из нашего ресторана.',
        reply_markup=start_markup()
    )
    # Регистрируем обработчик следующего шага
    bot.register_next_step_handler(msg, lambda m: start_perform_actions(m, bot))

def basket_message(message, bot):
    """
    Отправляет сообщение с содержимым корзины.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    msg = bot.send_message(
            message.chat.id,
            f'\U0001F6D2', reply_markup=start_markup())
    display_order(message, bot)
    bot.register_next_step_handler(msg, lambda m: start_perform_actions(m, bot))


def feedback_message(message, bot):
    """
    Отправляет сообщение с предложением оставить отзыв.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    user_id = message.from_user.id
    if user.user_exists(user_id):
        bot.send_message(
            message.chat.id,
            f'Здравствуйте, {message.from_user.first_name}! Оставьте, пожалуйста, отзыв о нашем сервисе, выбрав категорию ниже.',
            reply_markup=feedback_markup()
        )
        # Регистрируем обработчик следующего шага
        bot.register_next_step_handler(message, lambda m: fb.choose_category(m, bot))
    else:

        bot.send_message(message.chat.id, 'Вы не можете оставлять отзыв если еше не '
                                          'пользовались нашим сервисом. Мы будем рады если вы '
                                          'воспользуетесь нашим сервисом.', reply_markup=start_markup())
        bot.register_next_step_handler(message, lambda m: start_perform_actions(m, bot))

def look_for_feedback(message, bot):
    """
    Отправляет сообщение с предложением посмотреть отзывы.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    bot.send_message(
        message.chat.id,
        f'Здравствуйте, {message.from_user.first_name}! Вот последние отзывы, о сервисах ресторана.',)

    fb.look_service_feedback(message, bot)
def support_message(message, bot):
    """
    Отправляет сообщение с предложением обратиться в поддержку.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    bot.send_message(
        message.chat.id,
        f'Здравствуйте, {message.from_user.first_name}! Здесь вы можете обратиться за поддержкой.'
    )


def feedback_markup():
    """
    Создает и возвращает разметку клавиатуры для выбора категории обратной связи.

    :return: объект ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    markup.add('О сервисе ресторана', 'О блюдах')
    return markup


def start_markup():
    """
    Создает и возвращает разметку клавиатуры для начального меню.

    :return: объект ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add('\U0001F4CB Посмотреть меню', f'\U0001F6D2 Корзина ({str(basket)})',
               '\U0001F6F5 Посмотреть статус заказа')
    return markup


def category_markup():
    """
    Создает и возвращает разметку клавиатуры с категориями меню.

    :return: объект ReplyKeyboardMarkup
    """
    categories = menu.categories()
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    buttons = [f'{emoji} {name}' for emoji, name in categories]
    button1 = types.KeyboardButton('Назад в основное меню')
    markup.add(*buttons)
    markup.add(button1)  # Добавляем кнопку "Назад в основное меню"
    return markup


def items_markup(category_name):
    """
    Создает и возвращает разметку клавиатуры с элементами меню для выбранной категории.

    :param category_name: название категории
    :return: объект ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
    # Загружаем список блюд из выбранной категории
    items_list = menu.items_by_category(category_name)  # Предполагается, что такая функция существует в menu
    # Создаем кнопки
    buttons = [f"{item_name}" for item_name in items_list]
    button1 = types.KeyboardButton('Назад в категории')
    markup.add(*buttons)
    markup.add(button1)
    return markup


def dish_markup(message, dish_id):
    print('dish_id', dish_id)
    """Creates and returns the inline keyboard markup with options for a dish."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить в корзину', callback_data=f"add_to_cart:{dish_id}"))
    markup.add(types.InlineKeyboardButton('Прочитать отзыв', callback_data=f'read_review:{message.text}'))
    return markup


def command_message(message, bot):
    """
    Обрабатывает команды пользователя и вызывает соответствующие функции.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    commands = {
        '/feedback': feedback_message,
        '/basket': basket_message,
        '/support': support_message,
        '/look_feedback':look_for_feedback,
        '/start': start_message
    }
    if message.text in commands:
        commands[message.text](message, bot)


def start_perform_actions(message, bot):
    if message.text == '📋 Посмотреть меню':
        msg = bot.send_message(
            message.chat.id,
            f'{message.from_user.first_name}! Выберите нужную категорию.',
            reply_markup=category_markup()
        )
        bot.register_next_step_handler(msg, lambda m: category_selected(m, bot))
    elif message.text.startswith('🛒 Корзина'):
        basket_message(message, bot)

    elif message.text == '\U0001F6F5 Посмотреть статус заказа':
        bot.send_message(message.chat.id, 'Функция статус заказа')

    else:
        if message.text in ['/start', '/basket', '/feedback','/look_feedback', '/support']:
            command_message(message, bot)




def category_selected(message, bot):
    """
    Обрабатывает выбор категории пользователем.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    try:
        if message.text == 'Назад в основное меню':
            msg = bot.send_message(message.chat.id, 'Выберите дальнейшее действие:', reply_markup=start_markup())
            bot.register_next_step_handler(msg, lambda m: start_perform_actions(m, bot))
        else:
            category_name = message.text.split(' ', 1)[1]  # Извлекаем название категории из текста кнопки
            msg = bot.send_message(
                message.chat.id,
                f'Вы выбрали категорию: {category_name}. Выберите блюдо:',
                reply_markup=items_markup(category_name)
            )
            bot.register_next_step_handler(msg, lambda m: dish_selected(m, bot))
    except (IndexError, ValueError):
        if message.text in ['/start','/basket', '/feedback','/look_feedback', '/support']:
            command_message(message, bot)
        else:
            bot.send_message(message.chat.id, 'Ошибка ввода.', reply_markup=start_markup())
            bot.register_next_step_handler(message, lambda m: start_perform_actions(m, bot))


def dish_selected(message, bot):
    """
    Обрабатывает выбор блюда пользователем.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    user_id = message.from_user.id

    if message.text == 'Назад в категории':
        msg = bot.send_message(
            message.chat.id,
            f'{message.from_user.first_name}! Выберите нужную категорию.',
            reply_markup=category_markup()
        )
        bot.register_next_step_handler(msg, lambda m: category_selected(m, bot))

    elif message.text in ['/start','/basket', '/feedback','/look_feedback', '/support']:
        command_message(message, bot)

    else:
        dish_name = message.text
        details = menu.dish_details(dish_name)
        if details:
            dish_id, description, price, image_url = details
            caption = f"{dish_name}\n\n{description}\n\nЦена: {price} руб."

            # Отправляем новое сообщение с фото
            with open(image_url, 'rb') as photo:
                msg = bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=dish_markup(message, dish_id)
                )
        bot.register_next_step_handler(message, lambda m: dish_selected(m, bot))


def add_to_order(message, dish_id, order, bot):
    for position in order.positions:
        if position.dish_id == dish_id:
            bot.send_message(message.chat.id, "Блюдо уже есть в заказе. Вы можете отредактировать количество в корзине.")
            return
    #bot.send_message(message.chat.id, "Введите количество:")

    #bot.register_next_step_handler(message, lambda m: process_amount(m, dish_id, order, bot))
    process_amount(message, dish_id, order, bot)
def process_amount(message, dish_id, order, bot):
    db = Database('EasyEats.db')
    try:
        #amount = int(message.text)
        amount = 1
        if amount <= 0:
            raise ValueError("Количество должно быть больше нуля.")
        #menu_item = db.cursor.execute("SELECT price FROM menu WHERE dish_id = ?", (dish_id,)).fetchone()
        menu_item = db.get_dish(dish_id)
        if menu_item:
            price = menu_item[4]
            name = menu_item[2]
            #db.add_order_position(order.order_id, dish_id, price, amount)
            position = Position(dish_id, amount, price)
            order.add_position(position)
            bot.send_message(message.chat.id, f"Блюдо {name} добавлено в корзину.")
            #####
            #show_order(message, bot, order)
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

def basket_markup(order):
    db = Database('EasyEats.db')
    ind = 0
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for order in order.positions:
        menu_item = db.get_dish(order.dish_id)
        dish_name = menu_item[2]
        ind += 1
        print(order.dish_id)
        markup.add(f'{ind}. {dish_name}')
    return markup

def change_markup():
    markup = fb.feedback_score_markup()
    button = ['Другое число']
    markup.add(*button)
    return markup
def show_order(message, bot, order):
    db = Database('EasyEats.db')

    if not order.positions:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")
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


def process_delete(message, bot, order):
    try:
        pos_id = int(message.text[0])
        print(pos_id)

        # user_id = message.from_user.id
        # order = user_data[user_id]['order']
        pos_for_delete = order.positions[pos_id-1]

        order.remove_position(pos_for_delete)
        #db.delete_order_position(pos_id)
        bot.send_message(message.chat.id, "Позиция удалена из заказа.", reply_markup=start_markup())
        display_order(message, bot)
        bot.register_next_step_handler(message, lambda m: start_perform_actions(m, bot))

    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный № позиции.")


    # Обработчик команды /confirm для подтверждения заказа
    @bot.message_handler(commands=['confirm'])
    def confirm_order(message):
        bot.send_message(message.chat.id, "Ваш заказ подтвержден. Спасибо за покупку!")

def process_change(message, bot, order):
    try:
        pos_id = int(message.text[0])
        pos_for_change = order.positions[pos_id-1]
        bot.send_message(message.chat.id, "Выберете новое количество:", reply_markup=change_markup())
        bot.register_next_step_handler(message, lambda m: process_change_amount(m, bot, order, pos_for_change))

    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный № позиции.")

def process_change_amount(message, bot, order, position):
    db = Database('EasyEats.db')
    try:
        if message.text.strip().lower() == "другое число":
            bot.send_message(message.chat.id, "Введите нужное количество.")
            bot.register_next_step_handler(message, lambda m: process_change_amount(m, bot, order, position))
        else:
            amount = int(message.text.strip())
            if amount <= 0:
                raise ValueError("Количество должно быть больше нуля.")
            position.change_amount(amount)
            order.recalculate_total_price()
            bot.send_message(message.chat.id, "Позиция изменена.", reply_markup=start_markup())
            display_order(message, bot)
            bot.register_next_step_handler(message, lambda m: start_perform_actions(m, bot))
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное количество.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")


def display_order(message, bot):
    try:
        user_id = message.from_user.id
        order = user_data[user_id]['order']
        show_order(message, bot, order)
    except KeyError:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")