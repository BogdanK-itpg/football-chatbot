import os
import sqlite3
from sqlite3 import Error

# Get the directory where this db.py file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "sql", "football.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "..", "sql", "schema.sql")

def initialize_database():
    """Create tables if they don't exist and populate with sample data"""
    db_exists = os.path.exists(DB_PATH)
    
    if not db_exists:
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
    
    # Insert sample clubs data
    sample_clubs = [
        ("Левски София", "София", 1914),
        ("ЦСКА София", "София", 1948),
        ("Ботев Пловдив", "Пловдив", 1912),
        ("Лудогорец Разград", "Разград", 1945),
        ("Черно море Варна", "Варна", 1913),
        ("Спартак Варна", "Варна", 1929),
        ("Локомотив Пловдив", "Пловдив", 1926),
        ("Берое Стара Загора", "Стара Загора", 1916)
    ]
    
    for club in sample_clubs:
        cursor.execute(
            "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
            club
        )
    
    # Insert sample players data
    sample_players = [
        # Levski Sofia players
        (1, "Иван Иванов", "1995-03-15", "България", "GK", 1, "Активен"),
        (1, "Петър Петров", "1998-07-22", "България", "DF", 4, "Активен"),
        (1, "Мария Георгиева", "1997-11-08", "България", "MF", 10, "Активен"),
        (1, "Александър Николов", "1996-01-30", "България", "FW", 9, "Активен"),
        (1, "Николай Костов", "1999-09-18", "България", "DF", 2, "Активен"),
        
        # CSKA Sofia players
        (2, "Георги Димитров", "1994-05-12", "България", "GK", 1, "Активен"),
        (2, "Димитър Иванов", "1997-12-25", "България", "MF", 8, "Активен"),
        (2, "Кристиян Стоянов", "1998-04-03", "България", "FW", 11, "Активен"),
        (2, "Васил Андреев", "1996-06-14", "България", "DF", 3, "Активен"),
        (2, "Радослав Недев", "1995-02-20", "България", "MF", 6, "Активен"),
        
        # Botev Plovdiv players
        (3, "Мартин Камиларов", "1996-02-14", "България", "GK", 1, "Активен"),
        (3, "Илия Илиев", "1995-08-20", "България", "DF", 5, "Активен"),
        (3, "Радослав Стоянов", "1999-10-11", "България", "MF", 7, "Активен"),
        (3, "Васил Лечков", "1997-06-06", "България", "FW", 9, "Активен"),
        (3, "Кирил Симов", "1998-03-12", "България", "DF", 2, "Активен"),
        
        # Ludogorets players
        (4, "Владислав Стоянов", "1995-01-18", "България", "GK", 1, "Активен"),
        (4, "Калоян Стоянов", "1998-03-25", "България", "DF", 2, "Активен"),
        (4, "Ивелин Попов", "1996-07-14", "България", "MF", 6, "Активен"),
        (4, "Клавдиу Кейсел", "1997-12-01", "Румъния", "FW", 10, "Активен"),
        (4, "Жуан Пауло", "1999-05-15", "Бразилия", "MF", 8, "Активен"),
        
        # Cherno More Varna players
        (5, "Димитър Манолов", "1994-11-22", "България", "GK", 1, "Активен"),
        (5, "Павел Виданов", "1998-01-15", "България", "DF", 4, "Активен"),
        (5, "Атанас Пиров", "1996-09-30", "България", "MF", 8, "Активен"),
        (5, "Иван Стоянов", "1999-05-05", "България", "FW", 11, "Активен"),
        (5, "Мартин Тодоров", "1997-04-22", "България", "DF", 3, "Активен"),
        
        # Spartak Varna players
        (6, "Георги Георгиев", "1995-08-10", "България", "GK", 1, "Активен"),
        (6, "Кристиян Камбулов", "1998-12-03", "България", "DF", 5, "Активен"),
        (6, "Александър Михалков", "1996-02-28", "България", "MF", 7, "Активен"),
        (6, "Борислав Димитров", "1999-07-19", "България", "FW", 10, "Активен"),
        
        # Lokomotiv Plovdiv players
        (7, "Иван Колев", "1994-06-25", "България", "GK", 1, "Активен"),
        (7, "Петър Стайков", "1997-11-14", "България", "DF", 4, "Активен"),
        (7, "Мартин Димитров", "1998-09-30", "България", "MF", 8, "Активен"),
        (7, "Николай Николов", "1996-01-08", "България", "FW", 9, "Активен"),
        (7, "Димитър Димитров", "1999-03-17", "България", "MF", 6, "Активен"),
        
        # Beroe Stara Zagora players
        (8, "Атанас Атанасов", "1995-10-12", "България", "GK", 1, "Активен"),
        (8, "Иван Иванов", "1998-07-23", "България", "DF", 3, "Активен"),
        (8, "Георги Попов", "1997-02-14", "България", "MF", 7, "Активен"),
        (8, "Кирил Кирилов", "1999-12-01", "България", "FW", 11, "Активен")
    ]
    
    for player in sample_players:
        cursor.execute(
            """INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            player
        )
    
    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully with sample data")

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


