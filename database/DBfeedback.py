import sqlite3
import feedback as fb



def add_feedback(user_id, dish_id, score, feedback_text):
    try:
        # Connect to the database
        conn = sqlite3.connect('EasyEats.db')
        cursor = conn.cursor()

        # Define the SQL query
        query = '''
        INSERT INTO feedback (user_id, dish_id, score, feedback)
        VALUES (?, ?, ?, ?)
        '''

        # Execute the query
        cursor.execute(query, (user_id, dish_id, score, feedback_text))

        # Commit the transaction
        conn.commit()



    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        if conn:
            conn.close()


def get_feedback_by_dish_id(dish_id):
    # Подключение к базе данных
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    # Получение среднего значения score для данного dish_id
    cursor.execute("SELECT AVG(score) FROM feedback WHERE dish_id = ?", (dish_id,))
    avg_score = cursor.fetchone()[0]

    # Получение последних 10 отзывов для данного dish_id
    cursor.execute("SELECT feedback, user_id FROM feedback WHERE dish_id = ? ORDER BY id DESC LIMIT 10", (dish_id,))
    last_10_feedbacks = cursor.fetchall()

    # Закрытие соединения с базой данных
    conn.close()

    return avg_score, last_10_feedbacks

def get_service_feedback():
    # Подключение к базе данных
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT AVG(score) FROM feedback WHERE dish_id IS NULL")
    service_avg_score = cursor.fetchone()[0]

    query = """
            SELECT user_id, feedback
            FROM feedback
            WHERE dish_id IS NULL
            ORDER BY id DESC LIMIT 10
            """
    cursor.execute(query,)

    # Получение последних 10 отзывов.
    service_last_10_feedbacks = cursor.fetchall()
    print(service_last_10_feedbacks)
    print(service_avg_score)
    # Закрытие соединения с базой данных
    conn.close()

    return service_avg_score, service_last_10_feedbacks