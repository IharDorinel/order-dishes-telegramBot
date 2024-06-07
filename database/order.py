# Функции для обращения в БД к таблице order_header

import telebot
import sqlite3
# from main import bot

# Класс для работы с базой данных
TOKEN = '7367715020:AAEZortk_qDiDFA28I7LfAYnnbLsX1loE48'

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
# @bot.message_handler(commands=['start'])
# def send_welcome(message):
#     bot.reply_to(message, "Добро пожаловать в наш ресторан! Используйте /menu для просмотра меню.")




# # Обработчик добавления блюда в заказ
# @bot.message_handler(func=lambda message: message.text.startswith('/dish_'))
# def add_to_order(message, dish_id):
#     dish_id = int(message.text.split('_')[1])
#     bot.send_message(message.chat.id, "Введите количество:")
#     bot.register_next_step_handler(message, lambda m: process_amount(m, dish_id))

# def send_message(chat_id, text):
#     url = f"https://api.telegram.org/bot{'7367715020:AAEZortk_qDiDFA28I7LfAYnnbLsX1loE48'}/sendMessage"
#     payload = {
#         'chat_id': chat_id,
#         'text': text
#     }
#     response = requests.post(url, data=payload)
#     return response

def add_to_order(message, dish_id):
    print('message', message.chat.id)
    try:
        chat_id = message.chat.id
        print(f'add_to_order: dish_id={dish_id}')
        print(f'message.chat.id={chat_id}')

        msg = bot.send_message(chat_id, 'Введите количество:')


        print('Message sent successfully')

        print("Registering next step handler...")
        bot.register_next_step_handler(msg, lambda msg: process_amount(msg, dish_id, bot))
        print(f"Next step handler registered for chat_id {chat_id} and dish_id {dish_id}.")

    except telebot.apihelper.ApiException as e:
        print(f'Telegram API Exception: {e}')
    except Exception as e:
        print(f'Ошибка в add_to_order: {e}')

def process_amount(message, dish_id):
    print("Entered process_amount")
    try:
        amount = int(message.text)
        bot.send_message(message.chat.id, f"Блюдо {dish_id} добавлено в корзину в количестве {amount}!")
        print(f"Processed amount: {amount} for dish_id: {dish_id}")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное количество.")
        print("ValueError in process_amount: некорректное количество")


def process_delete(message):
    try:
        pos_id = int(message.text)
        db.delete_order_position(pos_id)
        bot.send_message(message.chat.id, "Позиция удалена из заказа.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный ID позиции.")


