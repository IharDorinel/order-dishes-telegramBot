from database import menu
from telebot import types
import handlers
from database import DBfeedback


def feedback_score_markup():
    """
    Создает и возвращает разметку клавиатуры для оценки отзывов.

    :return: объект ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(row_width=5, one_time_keyboard=True, resize_keyboard=True)
    markup.add('1', '2', '3', '4', '5')
    return markup


def dish_category_markup(message, bot):
    """
    Отправляет сообщение с разметкой клавиатуры для выбора категории блюд.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Загружаем список категорий из базы данных
    categories_list = menu.categories()
    # Создаем кнопки
    buttons = [types.InlineKeyboardButton(f"{e+n}", callback_data=f"category:{n}") for e, n in categories_list]
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        'Пожалуйста, выберите категорию блюд, о которых вы хотите оставить отзыв:',
        reply_markup=markup
    )


def choose_category(message, bot):
    """
    Обрабатывает выбор категории обратной связи пользователем.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    """
    category = message.text

    try:
        if category == 'О сервисе ресторана':
            msg = bot.send_message(message.chat.id, f'Пожалуйста, напишите ваш отзыв {category.lower()}.')
            bot.send_message(
                message.chat.id,
                'Вы можете написать отзыв о доставке, работе поддержки и общие впечатления\n'
                'Ваше мнение важно для нас.'
            )
            bot.register_next_step_handler(msg, lambda msg: score_selected(msg, bot))

        elif category == 'О блюдах':
            dish_category_markup(message, bot)

        elif category.startswith('Вы выбрали категорию'):
            bot.edit_message_text(
                text=f'\u2B05 Вы вернулись в выбор категорий',
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=dish_category_markup(message, bot)
            )
        else:
            raise ValueError
    except ValueError:
        if category in ['/start', '/feedback', '/support']:
            handlers.command_message(message, bot)
        else:
            bot.send_message(message.chat.id, 'Ошибка ввода.')
            handlers.feedback_message(message, bot)


def dish_category(call, bot):
    """
    Обрабатывает выбор категории блюда пользователем.

    :param call: объект вызова от пользователя
    :param bot: объект бота для отправки сообщений
    """
    category_name = call.data.split(':')[1]
    items_list = menu.items_by_category(category_name)
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Создаем кнопки для каждого блюда в категории
    buttons = [types.InlineKeyboardButton(f"{item_name}", callback_data=f"dish:{item_name}") for item_name in
               items_list]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton('Назад', callback_data='back:'))

    bot.edit_message_text(
        text=f'Вы выбрали категорию: {category_name}. '
             f'Пожалуйста, выберите блюдо, о котором вы хотите оставить отзыв:',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )


def fb_dish_selected(call, bot):
    """
    Обрабатывает выбор конкретного блюда пользователем и запрашивает отзыв.

    :param call: объект вызова от пользователя
    :param bot: объект бота для отправки сообщений
    """
    dish_name = call.data.split(':')[1]
    dish_id = menu.get_dish_id_by_name(dish_name)
    msg = bot.send_message(
        call.message.chat.id,
        f'Пожалуйста, напишите ваш отзыв о блюде "{dish_name}".'
    )
    bot.register_next_step_handler(msg, lambda msg: score_selected(msg, bot, dish_id))


def score_selected(message, bot, dish_id=None):
    """
    Запрашивает у пользователя оценку для его отзыва.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    :param dish_id: идентификатор блюда (если имеется)
    """
    feedback_text = message.text
    if feedback_text in ['/start', '/feedback', '/support']:
        handlers.command_message(message, bot)
    else:
        msg = bot.send_message(message.chat.id, 'Поставьте пожалуйста оценку от 1 до 5.',
                               reply_markup=feedback_score_markup())
        bot.register_next_step_handler(msg, lambda msg: save_feedback(msg, bot, feedback_text, dish_id))


def save_feedback(message, bot, feedback_text, dish_id=None):
    """
    Сохраняет отзыв и оценку пользователя в базе данных.

    :param message: объект сообщения от пользователя
    :param bot: объект бота для отправки сообщений
    :param feedback_text: текст отзыва пользователя
    :param dish_id: идентификатор блюда (если имеется)
    """
    try:
        score = int(message.text)
        user = message.from_user
        user_id = user.id
        DBfeedback.add_feedback(user_id, dish_id, score, feedback_text)

        bot.send_message(user_id, 'Спасибо за вашу оценку и отзыв! Мы ценим ваше мнение.',
                         reply_markup=handlers.start_markup())
        bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))

    except ValueError:
        if message.text in ['/start', '/feedback', '/support']:
            handlers.command_message(message, bot)
        else:
            msg = bot.send_message(message.chat.id,
                                   'Вы ввели некорректное значение. Пожалуйста, введите число от 1 до 5.')
            bot.register_next_step_handler(msg, lambda msg: save_feedback(msg, bot, feedback_text, dish_id))
