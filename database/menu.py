# Функции для обращения в БД к таблицам menu, category
import sqlite3


def categories():
    """
    Функция для получения данных из таблицы category
    :return: список строк в формате 'emoji name
    """

    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    # Выполняем SQL-запрос для получения данных из таблицы category
    cursor.execute("SELECT emoji, name FROM category")

    # Извлекаем все результаты
    rows = cursor.fetchall()
    # Закрываем соединение с базой данных
    conn.close()

    # Формируем и возвращаем список строк в формате 'emoji name'
    return rows

def dishes():
    """
    Функция для получения данных из таблицы menu
    :return: список строк в формате 'category_id dish_name price'
    """

    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    # Выполняем SQL-запрос для получения данных из таблицы dish
    cursor.execute("SELECT category_id, dish_name, price FROM dish")

    # Извлекаем все результаты
    rows = cursor.fetchall()
    # Закрываем соединение с базой данных
    conn.close()

    # Формируем и возвращаем список строк в формате 'category_id dish_name price'
    return rows


def items_by_category(category_name):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    # Выполняем JOIN для получения блюд по имени категории
    query = """
    SELECT m.dish_name
    FROM menu m
    JOIN category c ON m.category_id = c.category_id
    WHERE c.name = ?
    """
    cursor.execute(query, (category_name,))
    items = cursor.fetchall()
    conn.close()

    return  [item[0] for item in items]

def dish_details(dish_name):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    query = """
    SELECT m.description, m.price, m.image_url
    FROM menu m
    WHERE m.dish_name = ?
    """
    cursor.execute(query, (dish_name,))
    details = cursor.fetchone()
    conn.close()

    return details