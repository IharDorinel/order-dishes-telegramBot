import sqlite3



def user_exists(user_id):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS(SELECT 1 FROM order_header WHERE user_id = ?) AS user_exists;", (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] == 1

def status_check(user_id):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT order_id, total_price, status, create_at, "
                   "payment_method FROM order_header WHERE user_id = ? AND status NOT IN (?, ?)", (user_id, 'Выполнен','Отменен'))
    result = cursor.fetchall()

    conn.close()

    return result

def admin_status_check():
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT order_id, total_price, status, create_at, payment_method 
        FROM order_header 
        WHERE status NOT IN (?, ?)
    """, ('Выполнен', 'Отменен'))
    result = cursor.fetchall()


    conn.close()

    return result