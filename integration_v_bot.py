import telebot
from oplata_zakaza import process_payment  # Импортируем функцию оплаты из файла oplata_zakaza.py

API_TOKEN = 'YOUR_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['pay'])
def handle_payment(message):
    # Пример данных для оплаты (в реальном приложении эти данные нужно получить от пользователя безопасным способом)
    user_id = message.from_user.id
    order_id = 12345  # Это должен быть реальный ID заказа из базы данных
    card_number = '4242424242424242'
    exp_month = 12
    exp_year = 2024
    cvc = '123'
    amount = 1000  # 1000 копеек = 10 рублей

    result = process_payment(user_id, order_id, card_number, exp_month, exp_year, cvc, amount)

    if result['status'] == 'success':
        bot.send_message(message.chat.id, f"Оплата успешна! Идентификатор платежа: {result['charge_id']}")
    else:
        bot.send_message(message.chat.id, f"Ошибка при оплате: {result['message']}")


bot.polling()

'''Импорт функции оплаты: Импортируем функцию process_payment из файла oplata_zakaza.py.
Команда /pay: Добавляем обработчик команды /pay, которая будет инициировать процесс оплаты.
Получение данных: Для примера используются предопределенные данные карты и суммы. В реальном приложении эти данные должны быть безопасно собраны у пользователя.
Вызов функции оплаты: Вызывается функция process_payment, и результат обработки оплаты отправляется пользователю через бота.
Безопасность
Обратите внимание, что в реальном приложении вам нужно будет обеспечить безопасность передачи и хранения данных о банковских картах. Использование защищенных соединений (например, HTTPS), безопасного ввода данных и соблюдение стандартов безопасности платежных данных (например, PCI DSS) крайне важно.'''