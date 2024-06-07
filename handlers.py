# Функции-обработчики для команд и нажатия кнопок
from database import menu
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
        f'Здравствуйте, {message.from_user.first_name}! Я чат-бот, который поможет тебе сделать заказ еды.',
        reply_markup=start_markup()
    )
    # Регистрируем обработчик следующего шага
    bot.register_next_step_handler(msg, lambda m: start_perform_actions(m, bot))


def feedback_message(message, bot):
    """
    Отправляет сообщение с предложением оставить отзыв.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    bot.send_message(
        message.chat.id,
        f'Здравствуйте, {message.from_user.first_name}! Оставьте, пожалуйста, отзыв о нашем сервисе, выбрав категорию ниже.',
        reply_markup=feedback_markup()
    )
    # Регистрируем обработчик следующего шага
    bot.register_next_step_handler(message, lambda m: fb.choose_category(m, bot))


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


def dish_markup(message):
    """
    Создает и возвращает разметку клавиатуры с опциями для выбранного блюда.

    :return: объект InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить в корзину', callback_data='add_to_cart'))
    markup.add(types.InlineKeyboardButton('Посмотреть отзывы', callback_data=f'read_review:{message.text}'))
    return markup


def command_message(message, bot):
    """
    Обрабатывает команды пользователя и вызывает соответствующие функции.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    commands = {
        '/feedback': feedback_message,
        '/support': support_message,
        '/start': start_message
    }
    if message.text in commands:
        commands[message.text](message, bot)


def start_perform_actions(message, bot):
    """
    Обрабатывает действия пользователя, выбранные в начальном меню.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
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
    elif message.text in ['/start', '/feedback', '/support']:
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
        if message.text in ['/start', '/feedback', '/support']:
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

    elif message.text in ['/start', '/feedback', '/support']:
        command_message(message, bot)

    else:
        dish_name = message.text
        details = menu.dish_details(dish_name)
        if details:
            description, price, image_url = details
            caption = f"{dish_name}\n\n{description}\n\nЦена: {price} руб."

            # Отправляем новое сообщение с фото
            with open(image_url, 'rb') as photo:
                msg = bot.send_photo(
                    message.chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=dish_markup(message)
                )

            # Сохраняем id отправленного сообщения для последующего редактирования
            # message_manager.add_message(user_id, msg.message_id)
            bot.register_next_step_handler(msg, lambda m: dish_selected(m, bot))
        else:
            # В случае отсутствия информации о блюде, возвращаем сообщение об ошибке
            msg = bot.send_message(
                message.chat.id,
                "Извините, информация о данном блюде не найдена. Пожалуйста, выберите другое блюдо."
            )
            bot.register_next_step_handler(msg, lambda m: dish_selected(m, bot))
