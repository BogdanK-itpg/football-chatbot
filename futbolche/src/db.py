import os
import sqlite3
from sqlite3 import Error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "sql", "football.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "..", "sql", "schema.sql")
MIGRATION_PATH = os.path.join(BASE_DIR, "..", "sql", "migration.sql")

MIGRATION_FLAG_TABLE = "_migration_done"

def initialize_database():
    """Create tables if they don't exist and populate with sample data."""
    db_exists = os.path.exists(DB_PATH)

    if not db_exists:
        print(f"[DB] Creating new database at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())

        _insert_sample_data(conn, cursor)
        conn.commit()
        conn.close()
        print("[DB] Database initialized successfully with sample data")
        return

    # Database exists — run migration if not already done
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (MIGRATION_FLAG_TABLE,))
    if not cursor.fetchone():
        print("[DB] Running schema migration...")
        _run_migration(conn, cursor)
        print("[DB] Migration complete.")
    conn.close()


def _run_migration(conn, cursor):
    """Apply migration.sql to add new columns to existing tables."""
    migration_path = MIGRATION_PATH
    if os.path.exists(migration_path):
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        # Execute statement by statement (executescript can fail on some ALTER quirks)
        for statement in sql.split(';'):
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    # Column may already exist — ignore
                    print(f"[DB] Migration note (safe to ignore): {e}")
    # Mark migration as done
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {MIGRATION_FLAG_TABLE} (done INTEGER)")
    cursor.execute(f"INSERT INTO {MIGRATION_FLAG_TABLE} (done) VALUES (1)")
    conn.commit()


def _insert_sample_data(conn, cursor):
    """Populate new database with sample clubs, players, matches, and events."""

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
            "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)", club
        )

    sample_players = [
        (1, "Иван Иванов", "1995-03-15", "България", "GK", 1, "Активен"),
        (1, "Петър Петров", "1998-07-22", "България", "DF", 4, "Активен"),
        (1, "Мария Георгиева", "1997-11-08", "България", "MF", 10, "Активен"),
        (1, "Александър Николов", "1996-01-30", "България", "FW", 9, "Активен"),
        (1, "Николай Костов", "1999-09-18", "България", "DF", 2, "Активен"),
        (2, "Георги Димитров", "1994-05-12", "България", "GK", 1, "Активен"),
        (2, "Димитър Иванов", "1997-12-25", "България", "MF", 8, "Активен"),
        (2, "Кристиян Стоянов", "1998-04-03", "България", "FW", 11, "Активен"),
        (2, "Васил Андреев", "1996-06-14", "България", "DF", 3, "Активен"),
        (2, "Радослав Недев", "1995-02-20", "България", "MF", 6, "Активен"),
        (3, "Мартин Камиларов", "1996-02-14", "България", "GK", 1, "Активен"),
        (3, "Илия Илиев", "1995-08-20", "България", "DF", 5, "Активен"),
        (3, "Радослав Стоянов", "1999-10-11", "България", "MF", 7, "Активен"),
        (3, "Васил Лечков", "1997-06-06", "България", "FW", 9, "Активен"),
        (3, "Кирил Симов", "1998-03-12", "България", "DF", 2, "Активен"),
        (4, "Владислав Стоянов", "1995-01-18", "България", "GK", 1, "Активен"),
        (4, "Калоян Стоянов", "1998-03-25", "България", "DF", 2, "Активен"),
        (4, "Ивелин Попов", "1996-07-14", "България", "MF", 6, "Активен"),
        (4, "Клавдиу Кейсел", "1997-12-01", "Румъния", "FW", 10, "Активен"),
        (4, "Жуан Пауло", "1999-05-15", "Бразилия", "MF", 8, "Активен"),
        (5, "Димитър Манолов", "1994-11-22", "България", "GK", 1, "Активен"),
        (5, "Павел Виданов", "1998-01-15", "България", "DF", 4, "Активен"),
        (5, "Атанас Пиров", "1996-09-30", "България", "MF", 8, "Активен"),
        (5, "Иван Стоянов", "1999-05-05", "България", "FW", 11, "Активен"),
        (5, "Мартин Тодоров", "1997-04-22", "България", "DF", 3, "Активен"),
        (6, "Георги Георгиев", "1995-08-10", "България", "GK", 1, "Активен"),
        (6, "Кристиян Камбулов", "1998-12-03", "България", "DF", 5, "Активен"),
        (6, "Александър Михалков", "1996-02-28", "България", "MF", 7, "Активен"),
        (6, "Борислав Димитров", "1999-07-19", "България", "FW", 10, "Активен"),
        (7, "Иван Колев", "1994-06-25", "България", "GK", 1, "Активен"),
        (7, "Петър Стайков", "1997-11-14", "България", "DF", 4, "Активен"),
        (7, "Мартин Димитров", "1998-09-30", "България", "MF", 8, "Активен"),
        (7, "Николай Николов", "1996-01-08", "България", "FW", 9, "Активен"),
        (7, "Димитър Димитров", "1999-03-17", "България", "MF", 6, "Активен"),
        (8, "Атанас Атанасов", "1995-10-12", "България", "GK", 1, "Активен"),
        (8, "Иван Иванов", "1998-07-23", "България", "DF", 3, "Активен"),
        (8, "Георги Попов", "1997-02-14", "България", "MF", 7, "Активен"),
        (8, "Кирил Кирилов", "1999-12-01", "България", "FW", 11, "Активен")
    ]
    for player in sample_players:
        cursor.execute(
            "INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            player
        )

    # Sample matches with is_played = 1 (all have scores)
    sample_matches = [
        (1, 2, 2, 1, '2025-08-01'),
        (1, 3, 0, 0, '2025-08-08'),
        (2, 3, 1, 3, '2025-08-15'),
        (4, 5, 1, 2, '2025-08-02'),
        (6, 7, 0, 1, '2025-08-03'),
        (8, 7, 2, 2, '2025-08-04'),
        (2, 4, 3, 1, '2025-08-05'),
        (3, 5, 1, 1, '2025-08-06'),
    ]
    match_ids = []
    for hm, aw, hg, ag, dt in sample_matches:
        cursor.execute(
            "INSERT INTO matches (home_team_id, away_team_id, home_goals, away_goals, match_date, is_played) VALUES (?, ?, ?, ?, ?, 1)",
            (hm, aw, hg, ag, dt)
        )
        match_ids.append(cursor.lastrowid)

    # Sample events with club_id
    def _get_player_id(full_name, club_id=None):
        if club_id:
            cursor.execute("SELECT id FROM players WHERE full_name = ? AND club_id = ?", (full_name, club_id))
        else:
            cursor.execute("SELECT id FROM players WHERE full_name = ?", (full_name,))
        row = cursor.fetchone()
        return row[0] if row else None

    m1, m2, m3, m4, m5, m6, m7, m8 = match_ids

    pid_ivan = _get_player_id("Иван Иванов", 1)
    if pid_ivan:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 23)", (m1, pid_ivan, 1))
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'appearance', 0)", (m2, pid_ivan, 1))

    pid_krist = _get_player_id("Кристиян Стоянов", 2)
    if pid_krist:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 67)", (m1, pid_krist, 2))

    pid_dim = _get_player_id("Димитър Иванов", 2)
    if pid_dim:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 54)", (m7, pid_dim, 2))

    pid_vasil = _get_player_id("Васил Лечков", 3)
    if pid_vasil:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 12)", (m3, pid_vasil, 3))
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'assist', 33)", (m3, pid_vasil, 3))

    pid_ip = _get_player_id("Ивелин Попов", 4)
    if pid_ip:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, card_type, minute) VALUES (?, ?, ?, 'yellow', 'Y', 77)", (m4, pid_ip, 4))

    pid_boris = _get_player_id("Борислав Димитров", 6)
    if pid_boris:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 85)", (m5, pid_boris, 6))

    seed_transfers_path = os.path.join(os.path.dirname(SCHEMA_PATH), "seed_transfers.sql")
    if os.path.exists(seed_transfers_path):
        with open(seed_transfers_path, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())


def get_connection():
    try:
        initialize_database()
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute('PRAGMA foreign_keys = ON')
        except Exception:
            pass
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
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
            if not results:
                return None
            return results
        conn.commit()
        return True
    except Error as e:
        print(f"[QUERY ERROR] {e}")
        return None
    finally:
        conn.close()


def connect():
    return get_connection()


def execute(query: str, params=(), commit: bool = True, conn=None):
    if conn is None:
        own_conn = get_connection()
        if not own_conn:
            return None
        try:
            cursor = own_conn.cursor()
            cursor.execute(query, params)
            if commit:
                own_conn.commit()
            lastrowid = cursor.lastrowid
            return lastrowid if lastrowid else True
        except Error as e:
            print(f"[DB EXECUTE ERROR] {e}")
            return None
        finally:
            own_conn.close()
    else:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            lastrowid = cursor.lastrowid
            return lastrowid if lastrowid else True
        except Error as e:
            print(f"[DB EXECUTE ERROR] {e}")
            return None


def fetch_all(query: str, params=()):
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"[DB FETCH_ALL ERROR] {e}")
        return []
    finally:
        conn.close()


def fetch_one(query: str, params=()):
    rows = fetch_all(query, params)
    if rows:
        return rows[0]
    return None


def commit(conn):
    try:
        if conn:
            conn.commit()
    except Exception:
        pass


def rollback(conn):
    try:
        if conn:
            conn.rollback()
    except Exception:
        pass
