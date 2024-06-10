import handlers
from database import user


def support_message_to_admin(message, bot):
    admin_id = user.get_admin_id()
    if not admin_id:
        bot.send_message(message.chat.id, "Ошибка: Администратор не найден.")
        return

    bot.send_message(message.chat.id, 'Опишите свою проблему.')
    bot.register_next_step_handler(message, lambda m: support_perform_actions(m, admin_id, bot))


# Функция обработки сообщения и отправки админу
def support_perform_actions(message, admin_id, bot):
    support_message = message.text
    try:
        bot.send_message(admin_id,
                         f'SUPPORT!!!: {message.from_user.first_name} user_id: {message.from_user.id} - {support_message}')
        bot.send_message(message.chat.id, "Ваше сообщение отправлено в поддержку.", reply_markup=handlers.start_markup(message))
    except Exception as e:
        print(f"Ошибка при отправке сообщения админу: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при отправке сообщения в поддержку.", reply_markup=handlers.start_markup(message))

    bot.register_next_step_handler(message, lambda m: handlers.start_perform_actions(m, bot))