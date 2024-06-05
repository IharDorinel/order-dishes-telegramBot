import telebot
import sqlite3

# Ваш токен от BotFather
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

bot = telebot.TeleBot(TOKEN)

# Класс для работы с базой данных
class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_menu(self):
        self.cursor.execute("SELECT * FROM menu")
        return self.cursor.fetchall()

    def add_order_position(self, order_id, dish_id, price, amount):
        total_price = price * amount
        self.cursor.execute("INSERT INTO order_position (order_id, dish_id, price, amount, total_price) VALUES (?, ?, ?, ?, ?)",
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
        bot.send_photo(message.chat.id, image_url, caption=f"{dish_name}\n{description}\nЦена: {price} руб.\n/dish_{dish_id}")

# Обработчик добавления блюда в заказ
@bot.message_handler(func=lambda message: message.text.startswith('/dish_'))
def add_to_order(message):
    dish_id = int(message.text.split('_')[1])
    bot.send_message(message.chat.id, "Введите количество:")
    bot.register_next_step_handler(message, lambda m: process_amount(m, dish_id))

def process_amount(message, dish_id):
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError("Количество должно быть больше нуля.")
        menu_item = db.cursor.execute("SELECT price FROM menu WHERE dish_id = ?", (dish_id,)).fetchone()
        if menu_item:
            price = menu_item[0]
            db.add_order_position(order.order_id, dish_id, price, amount)
            bot.send_message(message.chat.id, "Блюдо добавлено в заказ.")
        else:
            bot.send_message(message.chat.id, "Блюдо не найдено.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное количество.")

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

    # Запускаем бота
    bot.polling()