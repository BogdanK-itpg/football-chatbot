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
    """Populate new database with the presentation-ready demo dataset."""

    seed_demo_path = os.path.join(os.path.dirname(SCHEMA_PATH), "seed_demo.sql")
    if not os.path.exists(seed_demo_path):
        raise FileNotFoundError(f"Demo seed file not found: {seed_demo_path}")

    with open(seed_demo_path, 'r', encoding='utf-8') as f:
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
