# Функции для обращения в БД к таблице order_header
import sqlite3

import datetime

user_data = {}


# Класс для работы с базой данных

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

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

    def get_dish(self, dish_id):
        self.cursor.execute("SELECT * FROM menu WHERE dish_id = ?", (dish_id,))
        return self.cursor.fetchone()

    def save_order(self, order):
        sql = '''INSERT INTO order_header (user_id, total_price, adress, status, create_at, update_at, payment_method)
                     VALUES (?, ?, ?, ?, ?, ?, ?)'''
        order.create_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Дата и время создания заказа
        order.update_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Дата и время изменения заказа
        self.cursor.execute(sql, (
        order.user_telegram, order.total_price, order.address, order.status, order.create_at, order.update_at,
        order.payment_method))
        self.conn.commit()
        order_id = self.cursor.lastrowid
        self.save_order_position(order_id, order.positions)

    def save_order_position(self, order_id, positions):
        for position in positions:
            sql = '''INSERT INTO order_positions (order_id, dish_id, price, amount)
                         VALUES (?, ?, ?, ?)'''
            self.cursor.execute(sql, (order_id, position.dish_id, position.price, position.amount))
            self.conn.commit()

    def update_order_status(self, order_id, status):
        sql = '''UPDATE order_header SET status = ?, update_at = ? WHERE order_id = ?'''
        update_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Дата и время изменения заказа
        self.cursor.execute(sql, (status, update_at, order_id))
        self.conn.commit()


# Класс для хранения состояния текущего заказа
class Order:
    def __init__(self, user_telegram):  #
        # self.order_id = 1  # Уникальный идентификатор заказа
        # (в реальных приложениях создавать уникальный ID для каждого заказа)
        self.user_telegram = user_telegram
        self.positions = []
        self.total_price = 0
        self.address = ''
        self.status = 'Новый'
        self.payment_method = ''
        self.create_at = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")  # Дата и время создания заказа можно изменить при сохранении
        self.update_at = self.create_at

    def clear(self):
        self.positions = []
        self.total_price = 0
        self.payment_method = ''
        self.address = ''
        self.status = 'Новый'

    def add_position(self, position):
        self.positions.append(position)
        self.total_price += position.total_price

    def remove_position(self, position):
        self.positions.remove(position)
        self.total_price -= position.total_price

    def recalculate_total_price(self):
        self.total_price = 0
        for position in self.positions:
            self.total_price += position.total_price


class Position:
    def __init__(self, dish_id, amount, price):
        self.dish_id = dish_id
        self.amount = amount
        self.price = price
        self.total_price = amount * price

    def change_amount(self, new_amount):
        self.amount = new_amount
        self.total_price = new_amount * self.price


def update_order_status(order_id, new_status):
    db = sqlite3.connect('EasyEats.db')
    cursor = db.cursor()
    cursor.execute("UPDATE order_header SET status = ? WHERE order_id = ?", (new_status, order_id))
    db.commit()
    db.close()