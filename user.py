import telebot
import sqlite3
from telebot import types

# Telegram Bot Token
API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Создаем объект бота
bot = telebot.TeleBot(API_TOKEN)

# Класс для работы с базой данных
class Database:
    def __init__(self, db_name='EasyEats.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def update_address(self, user_id, address):
        # Вставка или обновление адреса пользователя
        self.cursor.execute('''
            INSERT INTO users (user_id, adress) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET adress=excluded.adress
        ''', (user_id, address))
        self.conn.commit()

    def get_address(self, user_id):
        # Получение адреса пользователя
        self.cursor.execute('SELECT adress FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

# Инициализация базы данных
db = Database('EasyEats.db')

user_states = {}
def set_state(self, user_id, state):
    self.user_states[user_id] = state

def get_state(self, user_id):
    return self.user_states.get(user_id)

# Функция для создания клавиатуры
def create_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_address = types.KeyboardButton('Введите адрес доставки')
    markup.add(btn_address)
    return markup

# Обработчик нажатия кнопки "Введите адрес доставки"
@bot.message_handler(func=lambda message: message.text == 'Введите адрес доставки')
def add_address(message):
    set_state(message.chat.id, 'waiting_for_address')
    bot.reply_to(message, 'Введите, пожалуйста, адрес для доставки')

@bot.message_handler(func=lambda message: get_state(message.chat.id) == 'waiting_for_address')
def receive_address(message):
    address = message.text
    db.update_address(message.chat.id, address)
    set_state(message.chat.id, 'address_confirm')

    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    btn_confirm = types.KeyboardButton('Подтверждаю')
    btn_change = types.KeyboardButton('Изменить')
    markup.add(btn_confirm, btn_change)

    bot.send_message(message.chat.id, f"Ваш адрес: {address}. Подтвердите или измените.", reply_markup=markup)

@bot.message_handler(func=lambda message: get_state(message.chat.id) == 'address_confirm')
def confirm_address(message):
    if message.text.lower() == 'подтверждаю':
        set_state(message.chat.id, None)
        bot.send_message(message.chat.id, "Адрес подтвержден. Перейдите к выбору способа оплаты.", reply_markup=create_main_menu())
    elif message.text.lower() == 'изменить':
        set_state(message.chat.id, 'waiting_for_address')
        bot.send_message(message.chat.id, "Пожалуйста, введите ваш новый адрес для доставки:")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки для подтверждения или изменения адреса.")


# Запускаем бота
bot.polling()