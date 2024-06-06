# Функции для обращения в БД к таблице order_header
import requests
import telebot
import sqlite3

# Класс для работы с базой данных
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

bot = telebot.TeleBot(TOKEN)


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_menu(self):
        self.cursor.execute("SELECT * FROM menu")
        return self.cursor.fetchall()

    def add_order_position(self, order_id, dish_id, price, amount):
        total_price = price * amount
        self.cursor.execute(
            "INSERT INTO order_position (order_id, dish_id, price, amount, total_price) VALUES (?, ?, ?, ?, ?)",
            (order_id, dish_id, price, amount, total_price))
        self.conn.commit()

    def get_order(self, order_id):
        self.cursor.execute("""
            SELECT menu.dish_name, order_position.amount, order_position.price, order_position.total_price
            FROM order_position
            JOIN menu ON order_position.dish_id = menu.dish_id
            WHERE order_position.order_id = ?
        """, (order_id,))
        return self.cursor.fetchall()

    def delete_order_position(self, pos_id):
        self.cursor.execute("DELETE FROM order_position WHERE pos_id = ?", (pos_id,))
        self.conn.commit()


# Инициализация базы данных
db = Database('EasyEats.db')


# Класс для хранения состояния текущего заказа
class Order:
    def __init__(self):
        self.order_id = 1  # Уникальный идентификатор заказа (в реальных приложениях создавать уникальный ID для каждого заказа)


order = Order()


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать в наш ресторан! Используйте /menu для просмотра меню.")


# Обработчик команды /menu
@bot.message_handler(commands=['menu'])
def show_menu(message):
    menu_items = db.get_menu()
    for item in menu_items:
        dish_id, category_id, dish_name, description, price, image_url = item
        bot.send_photo(message.chat.id, image_url,
                       caption=f"{dish_name}\n{description}\nЦена: {price} руб.\n/dish_{dish_id}")


# # Обработчик добавления блюда в заказ
# @bot.message_handler(func=lambda message: message.text.startswith('/dish_'))
# def add_to_order(message, dish_id):
#     dish_id = int(message.text.split('_')[1])
#     bot.send_message(message.chat.id, "Введите количество:")
#     bot.register_next_step_handler(message, lambda m: process_amount(m, dish_id))

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{'7367715020:AAEZortk_qDiDFA28I7LfAYnnbLsX1loE48'}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, data=payload)
    return response

def add_to_order(message, dish_id):
    print('message', message.chat.id)
    try:
        chat_id = message.chat.id
        print(f'add_to_order: dish_id={dish_id}')
        print(f'message.chat.id={chat_id}')

        # Отправка сообщения с использованием requests
        response = send_message(chat_id, 'Введите количество:')

        # Проверка ответа
        print(f'Response status code: {response.status_code}')
        print(f'Response text: {response.text}')

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        print('Message sent successfully')

        print("Registering next step handler...")
        bot.register_next_step_handler(message, process_amount)
        print(f"Next step handler registered for chat_id {chat_id} and dish_id {dish_id}.")

    except telebot.apihelper.ApiException as e:
        print(f'Telegram API Exception: {e}')
    except Exception as e:
        print(f'Ошибка в add_to_order: {e}')

def process_amount(message, dish_id):
    print("Entered process_amount")
    try:
        amount = int(message.text)
        response = send_message(message.chat.id, f"Блюдо {dish_id} добавлено в корзину в количестве {amount}!")
        print(f"Processed amount: {amount} for dish_id: {dish_id}")
    except ValueError:
        response = send_message(message.chat.id, "Пожалуйста, введите корректное количество.")
        print("ValueError in process_amount: некорректное количество")


# Обработчик команды /order для просмотра текущего заказа
@bot.message_handler(commands=['order'])
def show_order(message):
    order_items = db.get_order(order.order_id)
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
    bot.register_next_step_handler(message, process_delete)


def process_delete(message):
    try:
        pos_id = int(message.text)
        db.delete_order_position(pos_id)
        bot.send_message(message.chat.id, "Позиция удалена из заказа.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный ID позиции.")

    # Обработчик команды /confirm для подтверждения заказа
    @bot.message_handler(commands=['confirm'])
    def confirm_order(message):
        bot.send_message(message.chat.id, "Ваш заказ подтвержден. Спасибо за покупку!")
