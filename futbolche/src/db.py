import os
import sqlite3
from sqlite3 import Error

DB_PATH = "../sql/football.db"
SCHEMA_PATH = "../sql/schema.sql"

def initialize_database():
    """Create tables if they don't exist"""
    if not os.path.exists(DB_PATH):
        print(f"[DB] Creating new database at {DB_PATH}")
    else:
        # Check if tables exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clubs'")
        if cursor.fetchone():
            conn.close()
            return  # Database already initialized
        conn.close()

    # Read schema and create tables
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully")

def get_connection():
    try:
        # Ensure database is initialized
        initialize_database()
        
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


