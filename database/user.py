# Функции для обращения в БД к таблице users
import sqlite3

def get_user(telegram_id):
    conn = sqlite3.connect('EasyEats.db', check_same_thread=False)
    cursor = conn.cursor()
    sql = '''SELECT * FROM users WHERE telegram = ?'''
    cursor.execute(sql, (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_user(order):
    conn = sqlite3.connect('EasyEats.db', check_same_thread=False)
    cursor = conn.cursor()
    # проверим есть ли такой пользователь
    sql = '''SELECT * FROM users WHERE telegram = ?'''
    cursor.execute(sql, (order.user_telegram,))
    user = cursor.fetchone()
    if user:     # обновим запись
        sql = '''UPDATE users SET adress = ? WHERE telegram = ?'''
        cursor.execute(sql, (order.address, order.user_telegram))
        conn.commit()
        conn.close()
        return
    else:      # добавим запись
        sql = '''INSERT INTO users (admin,telegram, adress) VALUES (?, ?, ?)'''
        cursor.execute(sql, (0, order.user_telegram, order.address))
        conn.commit()
        conn.close()

import sqlite3


def user_exists(user_id):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?) AS user_exists;", (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] == 1
