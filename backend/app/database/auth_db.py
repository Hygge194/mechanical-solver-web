from database.mysql_db import get_db_connection

def create_user(username: str, password_hash: str, full_name: str = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "INSERT INTO Users (Username, PasswordHash, FullName) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password_hash, full_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_by_username(username: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM Users WHERE Username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
