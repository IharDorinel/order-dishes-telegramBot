import handlers
from database import DBstaus


def staus_check(message, bot):
    if DBstaus.user_exists(message.from_user.id):

        order_status = DBstaus.staus_check(message.from_user.id)
        if order_status:
            order_id, total_price, status, create_at, payment_method = order_status
            response = (f"Ваш заказ #{order_id}:\n"
                            f"Статус: {status}\n"
                            f"Сумма: {total_price}\n"
                            f"Дата создания: {create_at}\n"
                            f"Метод оплаты: {payment_method}")

        bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))

    else:
        bot.send_message(message.chat.id, 'Вас нет в базе данных, возможно вы не делали заказ в нашем боте.'
                                          'Если это не так, то обратитесь в поддержку через команду /support '
                                          'в командном меню чата.', reply_markup=handlers.start_markup(message))
        bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))

