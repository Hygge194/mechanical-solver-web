import mysql.connector
from database.config import DB_CONFIG


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_motor_by_power(p_min):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT *
        FROM Thu_Vien_Dong_Co
        WHERE CongSuat_kW >= %s
        ORDER BY CongSuat_kW ASC, TocDo_vph DESC
        LIMIT 5
    """

    cursor.execute(query, (p_min,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def fetch_motor_by_power_and_speed(p_min, n_sb):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            Model as code,
            CongSuat_kW as P,
            TocDo_vph as n,
            CosPhi as cosphi,
            Tk_Tdn as tk_tdn
        FROM Thu_Vien_Dong_Co
        WHERE CongSuat_kW >= %s
        ORDER BY ABS(TocDo_vph - %s) ASC,
                 CongSuat_kW ASC
        LIMIT 3
    """

    cursor.execute(query, (p_min, n_sb))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results