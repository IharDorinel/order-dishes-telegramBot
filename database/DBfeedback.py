import sqlite3

import feedback as fb



def add_feedback(user_id, dish_id, feedback_text):
    try:
        # Connect to the database
        conn = sqlite3.connect('EasyEats.db')
        cursor = conn.cursor()

        # Define the SQL query
        query = '''
        INSERT INTO feedback (user_id, dish_id, feedback)
        VALUES (?, ?, ?)
        '''

        # Execute the query
        cursor.execute(query, (user_id, dish_id, feedback_text))

        # Commit the transaction
        conn.commit()

        print(f"Feedback from user {user_id} for dish {dish_id} saved successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        if conn:
            conn.close()