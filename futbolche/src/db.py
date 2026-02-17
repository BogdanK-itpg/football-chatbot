import os
import sqlite3
from sqlite3 import Error

DB_PATH = "../sql/football.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None


def execute_query(query, params=(), fetch=False):
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if fetch:
            results = cursor.fetchall()
            return results

        conn.commit()
        return True

    except Error as e:
        print(f"[QUERY ERROR] {e}")
        return None

    finally:
        conn.close()


