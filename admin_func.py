import handlers
from database import user, order, DBstatus
from telebot import types


# Функция для отображения админ-панели
def admin_message(message, bot):
    user_id = message.from_user.id
    if user.is_admin(user_id):
        bot.send_message(message.chat.id, "\U0001F6E0")
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        markup.add('Написать сообщение клиенту', 'Изменить статус заказа', 'Вернуться в главное меню')
        bot.send_message(
            message.chat.id,
            "Добро пожаловать в админ-панель. Выберите действие:",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, lambda m: admin_perform_actions(m, bot))

    else:

        bot.send_message(message.chat.id, "У вас нет прав доступа к этой команде.")


def admin_perform_actions(message, bot):
    if message.text == 'Написать сообщение клиенту':
        send_message_command(message, bot)

    elif message.text.startswith('Изменить статус заказа'):
        order_choose(message, bot)

    elif message.text == 'Вернуться в главное меню':
        msg = bot.send_message(message.chat.id, 'Выберите дальнейшее действие:',
                               reply_markup=handlers.start_markup(message))
        bot.register_next_step_handler(msg, lambda m: handlers.start_perform_actions(m, bot))
    else:
        if message.text in ['/start', '/basket', '/feedback', '/look_feedback', '/admin', '/support']:
            handlers.command_message(message, bot)


def order_choose(message, bot):
    order_statuses = DBstatus.admin_status_check()
    bot.send_message(message.chat.id, "\U0001F6F5")

    if order_statuses:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=False)
        buttons = [
            f"Номер заказа: #{order_id}, статус: {status}, дата заказа: {create_at}, оплата: {payment_method}"
            for order_id, total_price, status, create_at, payment_method in order_statuses
        ]
        markup.add(*buttons)

        msg = bot.send_message(message.chat.id, "Выберите нужный заказ.", reply_markup=markup)
        bot.register_next_step_handler(msg, lambda m: handle_order_selection(m, bot))
    else:
        bot.send_message(message.chat.id, "У вас нет активных заказов.")
        msg = bot.send_message(message.chat.id, 'Выберите дальнейшее действие:', reply_markup=handlers.start_markup(message))
        bot.register_next_step_handler(msg, lambda m: handlers.start_perform_actions(m, bot))

def handle_order_selection(message, bot):
    try:
        selected_order_text = message.text
        order_id = int(selected_order_text.split('#')[1].split(',')[0].strip())

        change_order_status(message, order_id, bot)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Ошибка выбора заказа. Пожалуйста, попробуйте снова.")
        order_choose(message, bot)


def change_order_status(message,order_id, bot):
    try:
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        markup.add('Обрабатывается', 'В пути', 'Выполнен', 'Отменен')
        msg = bot.send_message(
            message.chat.id,
            "Выберите новый статус для заказа:",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, lambda m: update_order_status(m, order_id, bot))
    except ValueError:
        msg = bot.send_message(message.chat.id, "Неверный ввод. Попробуйте ещё раз.")
        bot.register_next_step_handler(msg, lambda m: change_order_status(m, bot))


def update_order_status(message, order_id, bot):
    new_status = message.text
    db = order.Database('EasyEats.db')
    db.update_order_status(order_id, new_status)
    db.close()
    user_id = user.get_user_id(order_id)
    bot.send_message(message.chat.id, f"Статус заказа #{order_id} изменен на '{new_status}'.", reply_markup=handlers.start_markup(message))
    bot.send_message(user_id, "\U0001F6F5")
    bot.send_message(user_id, f"Статус вашего заказа #{order_id} изменен на '{new_status}'.")
    bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))


def send_message_command(message, bot):
    bot.send_message(message.chat.id, "Введите user_id пользователя, которому вы хотите отправить сообщение.")
    bot.register_next_step_handler(message, lambda m: get_user_id(m, bot))


def get_user_id(message, bot):
    try:
        user_id = int(message.text)
        bot.send_message(message.chat.id, "Введите сообщение для пользователя.")
        bot.register_next_step_handler(message, lambda m: send_message_to_user(m, user_id, bot))
    except Exception as e:
        print(f"Ошибка при получении user_id: {e}")
        bot.send_message(message.chat.id, "Некорректный user_id. Попробуйте еще раз.")
        bot.register_next_step_handler(message, lambda m: get_user_id(m, bot))


def send_message_to_user(message, user_id, bot):
    user_message = message.text
    try:
        bot.send_message(user_id, f"SUPPORT!!!:\nСообщение от администратора: {user_message}")
        bot.send_message(message.chat.id, "Сообщение успешно отправлено.", reply_markup=handlers.start_markup(message))

    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при отправке сообщения.", reply_markup=handlers.start_markup(message))

    bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))