from database import menu
from telebot import types
import handlers
from database import DBfeedback


def feedback_score_markup():
    """
    Creates and returns the reply keyboard markup for feedback categories.
    """
    markup = types.ReplyKeyboardMarkup(row_width=5, one_time_keyboard=True, resize_keyboard=True)
    markup.add('1', '2', '3', '4', '5')
    return markup


def dish_category_markup(message, bot):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Load list of categories from the database
    categories_list = menu.categories()
    # Create buttons
    buttons = [types.InlineKeyboardButton(f"{e + n}", callback_data=f"category:{n}") for e, n in categories_list]
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        'Пожалуйста, выберите категорию блюд, о которых вы хотите оставить отзыв:',
        reply_markup=markup
    )


def choose_category(message, bot):
    """
    Handles the user's choice of feedback category.
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

        elif category.split(':')[0] == 'Вы выбрали категорию':
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
    Handles the user's choice of dish category.
    """
    category_name = call.data.split(':')[1]
    items_list = menu.items_by_category(category_name)
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Create buttons for each item in the category
    buttons = [types.InlineKeyboardButton(f"{item_name}",
                                          callback_data=f"dish:{item_name}")
               for item_name in items_list]
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
    Handles the user's choice of a specific dish and asks for feedback.
    """
    dish_name = call.data.split(':')[1]
    dish_id = menu.get_dish_id_by_name(dish_name)
    msg = bot.edit_message_text(
        text=f'Пожалуйста, напишите ваш отзыв о блюде "{dish_name}".',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,

    )
    bot.register_next_step_handler(msg, lambda msg: score_selected(msg, bot, dish_id))


def score_selected(message, bot, dish_id=None):
    """
    Asks the user to provide a score for their feedback.
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
    Saves the user's feedback and score in the database.
    """
    try:
        score = int(message.text)
        user = message.from_user
        user_id = user.id
        DBfeedback.add_feedback(user_id, dish_id, score, feedback_text)

        bot.send_message(user_id, 'Спасибо за вашу оценку и отзыв! Мы ценим ваше мнение.', reply_markup=handlers.start_markup())
        bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))

    except ValueError:
        if message.text in ['/start', '/feedback', '/support']:
            handlers.command_message(message, bot)
        else:
            msg = bot.send_message(message.chat.id, 'Вы ввели некорректное значение. Пожалуйста, введите число от 1 до 5.')
            bot.register_next_step_handler(msg, lambda msg: save_feedback(msg, bot, feedback_text, dish_id))