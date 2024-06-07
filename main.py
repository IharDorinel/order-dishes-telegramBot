import telebot
import feedback as fb
import handlers
from database import order as ord



bot = telebot.TeleBot('7367715020:AAEZortk_qDiDFA28I7LfAYnnbLsX1loE48')

commands = [
    telebot.types.BotCommand('/start', 'Запустить бота'),
    telebot.types.BotCommand('/feedback', 'Оставить отзыв'),
    telebot.types.BotCommand('/support', 'Обратиться в поддержку')
]

bot.set_my_commands(commands)


@bot.message_handler(commands=['start'])
def start_message(message):
    handlers.start_message(message, bot)


@bot.message_handler(commands=['feedback'])
def start_message(message):
    handlers.feedback_message(message, bot)


@bot.message_handler(commands=['support'])
def start_message(message):
    handlers.support_message(message, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('category:'))
def choose_dish_category(call):
    fb.dish_category(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dish:'))
def choose_dish(call):
    fb.fb_dish_selected(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart'))
def handle_callback(call):
    print('call', call.message)
    dish_id = call.data.split(':')[1]
    user_id = call.from_user.id
    if user_id not in ord.user_data:
        ord.user_data[user_id] = {'order': ord.Order(user_id)}
    order = ord.user_data[user_id]['order']
    handlers.add_to_order(call.message, dish_id, order, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_position'))
def delete_from_order(call):
    user_id = call.from_user.id
    order = ord.user_data[user_id]['order']
    bot.send_message(call.message.chat.id, "Введите № позиции для удаления:")
    bot.register_next_step_handler(call.message, lambda m: handlers.process_delete(m, bot, order))

@bot.callback_query_handler(func=lambda call: call.data.startswith('change_position'))
def change_order(call):
    user_id = call.from_user.id
    order = ord.user_data[user_id]['order']
    bot.send_message(call.message.chat.id, "Введите № позиции для изменения:")
    bot.register_next_step_handler(call.message, lambda m: handlers.process_change(m, bot, order))

@bot.callback_query_handler(func=lambda call: call.data.startswith('clear_cart'))
def clear_cart(call):
    user_id = call.from_user.id
    order = ord.user_data[user_id]['order']
    order.clear()
    bot.send_message(call.message.chat.id, "Корзина очищена")

@bot.callback_query_handler(func=lambda call: call.data.startswith('checkout'))
def checkout(call):
    user_id = call.from_user.id
    order = ord.user_data[user_id]['order']
    #order.clear() -- не забыть в функции которая будет финализировать заказ очистить корзину в конце



# Обработчик команды /menu
@bot.message_handler(commands=['menu'])
def show_menu(message):
    menu_items = order.db.get_menu()
    for item in menu_items:
        dish_id, category_id, dish_name, description, price, image_url = item
        bot.send_photo(message.chat.id, image_url,
                       caption=f"{dish_name}\n{description}\nЦена: {price} руб.\n/dish_{dish_id}")


# Обработчик команды /order для просмотра текущего заказа
@bot.message_handler(commands=['order'])
def show_order(message):
    order_items = order.db.get_order(order.order_id)
    if not order_items:
        bot.send_message(message.chat.id, "Ваш заказ пуст.")
    else:
        order_details = ""
        total_price = 0
        for item in order_items:
            dish_name, amount, price, item_total_price = item
            order_details += f"{dish_name} x{amount} - {price} руб. за шт. (Итого: {item_total_price} руб.)\n"
            total_price += item_total_price
        order_details += f"\nОбщая сумма заказа: {total_price} руб."
        bot.send_message(message.chat.id, order_details)

# Обработчик команды /delete для удаления позиции из заказа
@bot.message_handler(commands=['delete'])
def delete_from_order(message):
    bot.send_message(message.chat.id, "Введите ID позиции для удаления:")
    bot.register_next_step_handler(message, order.process_delete(message))

# Обработчик команды /confirm для подтверждения заказа
    @bot.message_handler(commands=['confirm'])
    def confirm_order(message):
        bot.send_message(message.chat.id, "Ваш заказ подтвержден. Спасибо за покупку!")

# Обработчик текстовых сообщений
# @bot.message_handler(func=lambda message: True)
# def handle_text(message):
#     print(f"Received message: {message.text}")
#     bot.send_message(message.chat.id, "Вы ввели текст: " + message.text)
#
# bot.polling(none_stop=True)
