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
    if user:  # обновим запись
        sql = '''UPDATE users SET address = ? WHERE telegram = ?'''
        cursor.execute(sql, (order.address, order.user_telegram))
        conn.commit()
        conn.close()
        return
    else:  # добавим запись
        sql = '''INSERT INTO users (admin,telegram, address) VALUES (?, ?, ?, ?)'''
        cursor.execute(sql, (0, order.user_telegram, order.address))
        conn.commit()
        conn.close()


def user_exists(user_id):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE telegram = ?) AS user_exists;", (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] == 1


def is_admin(user_id):
    db = sqlite3.connect('EasyEats.db')
    cursor = db.cursor()
    cursor.execute("SELECT admin FROM users WHERE telegram = ?", (user_id,))
    result = cursor.fetchone()
    print(result)
    db.close()
    return int(result[0]) == 1 if result else False


def get_admin_id():
    try:
        db = sqlite3.connect('EasyEats.db')
        cursor = db.cursor()
        cursor.execute("SELECT telegram FROM users WHERE admin = 1")
        result = cursor.fetchone()
        db.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return None

def get_user_id(order_id):
    db = sqlite3.connect('EasyEats.db')
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM order_header WHERE order_id = ?", (order_id,))
    result = cursor.fetchone()
    db.close()
    return result[0] if result else None

