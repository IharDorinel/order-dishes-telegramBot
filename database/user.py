# Функции для обращения в БД к таблице users
import sqlite3


def user_exists(user_id):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?) AS user_exists;", (user_id,))
    result = cursor.fetchone()


    conn.close()

    return result[0] == 1