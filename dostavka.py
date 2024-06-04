
from telebot import types




# Словарь для хранения адресов доставки пользователей
user_addresses = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    btn_delivery = types.KeyboardButton('Ввести адрес доставки')
    markup.add(btn_delivery)
    bot.send_message(message.chat.id, "Добро пожаловать! Пожалуйста, выберите опцию:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Ввести адрес доставки')
def request_address(message):
    msg = bot.send_message(message.chat.id, "Пожалуйста, введите свой адрес доставки заказа:")
    bot.register_next_step_handler(msg, save_address)


def save_address(message):
    user_id = message.from_user.id
    address = message.text
    user_addresses[user_id] = address
    bot.send_message(message.chat.id, f"Адрес доставки сохранен: {address}")


# @bot.message_handler(commands=['pay'])
# def handle_payment(message):
#     user_id = message.from_user.id
#     if user_id in user_addresses:
        # Пример данных для оплаты (в реальном приложении эти данные нужно получить от пользователя безопасным способом)
        # order_id = 12345  # Это должен быть реальный ID заказа из базы данных
        # card_number = '4242424242424242'
        # exp_month = 12
        # exp_year = 2024
        # cvc = '123'
        # amount = 1000  # 1000 копеек = 10 рублей

    #     from oplata_zakaza import process_payment  # Импорт функции оплаты
    #
    #     result = process_payment(user_id, order_id, card_number, exp_month, exp_year, cvc, amount)
    #
    #     if result['status'] == 'success':
    #         bot.send_message(message.chat.id, f"Оплата успешна! Идентификатор платежа: {result['charge_id']}")
    #     else:
    #         bot.send_message(message.chat.id, f"Ошибка при оплате: {result['message']}")
    # else:
    #     bot.send_message(message.chat.id,
    #                      "Пожалуйста, введите свой адрес доставки перед оплатой. Нажмите 'Ввести адрес доставки'."

'''Создание кнопки:

При старте бота с командой /start создается кнопка Ввести адрес доставки, которая добавляется в разметку сообщений.
При нажатии на кнопку вызывается функция request_address.
Запрос адреса:

Функция request_address отправляет сообщение с просьбой ввести адрес и регистрирует следующий обработчик шага для сохранения адреса.
Сохранение адреса:

Функция save_address сохраняет введенный адрес в словарь user_addresses по идентификатору пользователя.
Обработка оплаты:

В обработчике команды /pay проверяется, есть ли адрес доставки для текущего пользователя. Если адрес введен, происходит процесс оплаты.
Если адрес не введен, бот просит пользователя ввести адрес перед оплатой.
Таким образом, пользователи смогут сначала ввести свой адрес доставки, а затем, при необходимости, совершить оплату заказа.'''





