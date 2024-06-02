import sqlite3

def create_database():
    # Подключение к базе данных (создание файла базы данных)
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    # Отключение режима проверки целостности внешнего ключа для выполнения DDL-запросов
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # DDL-запросы для создания таблиц
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS category(
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin NOT NULL DEFAULT 0,
            telegram VARCHAR(255) NOT NULL,
            adress VARCHAR(255)
        );
        """,
        """
        CREATE TABLE menu(
            dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
            catgory_id INT NOT NULL,
            dish_name VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL,
            price DECIMAL(8, 2) NOT NULL,
            image_url VARCHAR(255),
            FOREIGN KEY (catgory_id) REFERENCES catgory(catgory_id)
        );
        """,
        """
        CREATE TABLE order_header(
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT NOT NULL,
            total_price DECIMAL(8, 2) NOT NULL,
            adress VARCHAR(255) NOT NULL,
            status VARCHAR(255) NOT NULL,
            create_at DATETIME NOT NULL,
            update_at DATETIME NOT NULL,
            payment_method VARCHAR(255) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """,
        """
        CREATE TABLE order_positions(
            pos_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INT NOT NULL,
            dish_id INT NOT NULL,
            price DECIMAL(8, 2) NOT NULL,
            amount INT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES order_header(order_id),
            FOREIGN KEY (dish_id) REFERENCES menu(dish_id)
        );
        """,
        """
        CREATE TABLE feedback(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT NOT NULL,
            dish_id INT NOT NULL,
            score INT NOT NULL,
            feedback TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (dish_id) REFERENCES menu(dish_id)
        );
        """
    ]

    # Выполнение DDL-запросов для создания таблиц
    for ddl in ddl_statements:
        cursor.execute(ddl)

    # Включение режима проверки целостности внешнего ключа
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Фиксация изменений, закрытие курсора и соединения с базой данных
    cursor.close()
    conn.commit()
    conn.close()


create_database()
print("Database created successfully.")