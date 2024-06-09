import telebot
import feedback as fb
import handlers
from database import order as ord

bot = telebot.TeleBot('6619304848:AAHLbyN5yN96nyYzGsL7PV8vo8uCuy_OTBc')

commands = [
    telebot.types.BotCommand('/start', 'Запустить бота'),
    telebot.types.BotCommand('/basket', 'Корзина'),
    telebot.types.BotCommand('/feedback', 'Оставить отзыв'),
    telebot.types.BotCommand('/look_feedback', 'Посмотреть отзывы о ресторане'),
    telebot.types.BotCommand('/support', 'Обратиться в поддержку')
]

bot.set_my_commands(commands)


@bot.message_handler(commands=['start'])
def start_message(message):
    handlers.start_message(message, bot)


@bot.message_handler(commands=['basket'])
def basket_message(message):
    handlers.basket_message(message, bot)


@bot.message_handler(commands=['feedback'])
def feedback_message(message):
    handlers.feedback_message(message, bot)


@bot.message_handler(commands=['look_feedback'])
def look_feedback_message(message):
    handlers.look_for_feedback(message, bot)


@bot.message_handler(commands=['support'])
def support_message(message):
    handlers.support_message(message, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith('category:'))
def choose_dish_category(call):
    fb.dish_category(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith('dish:'))
def choose_dish(call):
    fb.fb_dish_selected(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith('back:'))
def back_to_category(call):
    fb.choose_category(call.message, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith('read_review:'))
def read_dish_review(call):
    fb.read_dish_review(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart'))
def handle_callback(call):
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
    if not order.positions:
        bot.send_message(call.message.chat.id, "Ваша корзина пуста.")
    else:
        bot.send_message(call.message.chat.id, "Выберете позицию для удаления:",
                         reply_markup=handlers.basket_markup(order))
        bot.register_next_step_handler(call.message, lambda m: handlers.process_delete(m, bot, order))


@bot.callback_query_handler(func=lambda call: call.data.startswith('change_position'))
def change_order(call):
    user_id = call.from_user.id
    order = ord.user_data[user_id]['order']
    bot.send_message(call.message.chat.id, "Выберете позицию для изменения:",
                     reply_markup=handlers.basket_markup(order))
    bot.register_next_step_handler(call.message, lambda m: handlers.process_change(m, bot, order))


@bot.callback_query_handler(func=lambda call: call.data.startswith('clear_cart'))
def clear_cart(call):
    user_id = call.from_user.id
    order = ord.user_data[user_id]['order']
    order.clear()
    bot.send_message(call.message.chat.id, "Корзина очищена", reply_markup=handlers.start_markup(call.message))
    # handlers.basket_message(call.message, bot)
    # bot.register_next_step_handler(call.message, lambda m: handlers.start_perform_actions(m, bot))


@bot.callback_query_handler(func=lambda call: call.data.startswith('checkout'))
def checkout(call):
    user_id = call.from_user.id
    order = ord.user_data[user_id]['order']
    # order.clear() -- не забыть в функции которая будет финализировать заказ очистить корзину в конце


bot.polling(none_stop=True)
