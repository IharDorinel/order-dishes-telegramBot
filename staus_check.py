import handlers
from database import DBstatus


def status_check(message, bot):
    if DBstatus.user_exists(message.from_user.id):
        order_status = DBstatus.status_check(message.from_user.id)
        bot.send_message(message.chat.id, "\U0001F6F5")
        if order_status:
            all_orders = []
            for order_status in order_status:
                order_id, total_price, status, create_at, payment_method = order_status
                response = (f"Ваш заказ #{order_id}:\n"
                            f"Статус: {status}\n"
                            f"Сумма: {total_price}\n"
                            f"Дата создания: {create_at}\n"
                            f"Метод оплаты: {payment_method}")
                all_orders.append(response)
            response = '\n\n'.join(all_orders)

            bot.send_message(message.chat.id, response, reply_markup=handlers.start_markup(message))
        else:

            bot.send_message(message.chat.id, 'У вас нет активных заказов.\n'
                                              'Если это не так, то обратитесь в поддержку через команду /support '
                                              'в командном меню чата.', reply_markup=handlers.start_markup(message))
    else:

        bot.send_message(message.chat.id, 'Вас нет в базе данных, возможно вы не делали заказ в нашем боте.\n'
                                          'Если это не так, то обратитесь в поддержку через команду /support '
                                          'в командном меню чата.', reply_markup=handlers.start_markup(message))
    bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))
