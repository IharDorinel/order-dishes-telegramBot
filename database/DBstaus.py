import sqlite3



def user_exists(user_id):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS(SELECT 1 FROM order_header WHERE user_id = ?) AS user_exists;", (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] == 1

def staus_check(user_id):
    conn = sqlite3.connect('EasyEats.db')
    cursor = conn.cursor()

    cursor.execute("SELECT order_id, total_price, status, create_at, "
                   "payment_method FROM order_header WHERE user_id = ? AND status != ?", (user_id, 'Выполнен'))
    result = cursor.fetchone()

    conn.close()

    return result