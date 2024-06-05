from database import menu
from telebot import types


def choose_category(message, bot):
    category = message.text
    print(category)

    if category == 'О сервисе ресторана':
        msg = bot.send_message(message.chat.id, f'Пожалуйста, напишите ваш отзыв {category.lower()}.')
        msg = bot.send_message(message.chat.id, 'Вы можете написать о доставке, работе поддержки и общие впечатления\n '
                                                'Ваше мнение важно для нас.')
        bot.register_next_step_handler(msg, lambda msg: save_feedback(msg, bot))
    elif category == 'О блюдах':
        markup = types.InlineKeyboardMarkup(row_width=2)

        # Загружаем список категорий из БД
        categories_list = menu.categories()
        # Создаем кнопки
        buttons = [types.InlineKeyboardButton(f"{e+n}", callback_data=f"category:{n}") for e, n in
                   categories_list]
        markup.add(*buttons)

        bot.send_message(
            message.chat.id,
            'Пожалуйста, выберите категорию блюд, о которых вы хотите оставить отзыв:',
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, 'Неверная категория. Пожалуйста, выберите одну из предложенных категорий.')
        #feedback_message(message)


def dish_category(call, bot):
    category_name = call.data.split(':')[1]
    items_list = menu.items_by_category(category_name)
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(f"{item_name}", callback_data=f"dish:{item_name}") for item_name in
               items_list]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton('Назад', callback_data='category:' + category_name))

    bot.edit_message_text(
        text=f'Вы выбрали категорию: {category_name}. Пожалуйста, выберите блюдо, о котором вы хотите оставить отзыв:',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )


def fb_dish_selected(call, bot):
    print(call.data)
    dish_name = call.data.split(':')[1]
    dish_id = menu.get_dish_id_by_name(dish_name)
    print(dish_id)
    msg = bot.send_message(call.message.chat.id, f'Пожалуйста, напишите ваш отзыв о блюде "{dish_name}".')
    bot.register_next_step_handler(msg, lambda msg: save_feedback(msg, bot, dish_id))


def save_feedback(message, bot, dish_id=None):
    feedback_text = message.text
    user = message.from_user
    user_id = user.id

    add_feedback(user_id, dish_id, feedback_text)

    bot.send_message(user_id, 'Спасибо за ваш отзыв! Мы ценим ваше мнение.')

def add_feedback(user_id, dish_id, feedback_text):
    print(user_id, dish_id, feedback_text)
    pass