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

    # =============================================
    # 18 Clubs
    # =============================================
    sample_clubs = [
        ("Левски София", "София", 1914),
        ("ЦСКА София", "София", 1948),
        ("Ботев Пловдив", "Пловдив", 1912),
        ("Лудогорец Разград", "Разград", 1945),
        ("Черно море Варна", "Варна", 1913),
        ("Спартак Варна", "Варна", 1929),
        ("Локомотив Пловдив", "Пловдив", 1926),
        ("Берое Стара Загора", "Стара Загора", 1916),
        ("Славия София", "София", 1913),
        ("Локомотив София", "София", 1929),
        ("Арда Кърджали", "Кърджали", 1924),
        ("Ботев Враца", "Враца", 1921),
        ("Пирин Благоевград", "Благоевград", 1922),
        ("ЦСКА 1948 София", "София", 2016),
        ("Хебър Пазарджик", "Пазарджик", 1918),
        ("Крумовград", "Крумовград", 2021),
        ("Етър Велико Търново", "Велико Търново", 1924),
        ("Септември София", "София", 1944),
    ]
    for club in sample_clubs:
        cursor.execute(
            "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)", club
        )

    # =============================================
    # 90 Players (5 per club)
    # =============================================
    sample_players = [
        # Club 1 — Левски София
        (1, "Иван Иванов", "1995-03-15", "България", "GK", 1, "Активен"),
        (1, "Петър Петров", "1998-07-22", "България", "DF", 4, "Активен"),
        (1, "Мария Георгиева", "1997-11-08", "България", "MF", 10, "Активен"),
        (1, "Александър Николов", "1996-01-30", "България", "FW", 9, "Активен"),
        (1, "Николай Костов", "1999-09-18", "България", "DF", 2, "Активен"),
        # Club 2 — ЦСКА София
        (2, "Георги Димитров", "1994-05-12", "България", "GK", 1, "Активен"),
        (2, "Димитър Иванов", "1997-12-25", "България", "MF", 8, "Активен"),
        (2, "Кристиян Стоянов", "1998-04-03", "България", "FW", 11, "Активен"),
        (2, "Васил Андреев", "1996-06-14", "България", "DF", 3, "Активен"),
        (2, "Радослав Недев", "1995-02-20", "България", "MF", 6, "Активен"),
        # Club 3 — Ботев Пловдив
        (3, "Мартин Камиларов", "1996-02-14", "България", "GK", 1, "Активен"),
        (3, "Илия Илиев", "1995-08-20", "България", "DF", 5, "Активен"),
        (3, "Радослав Стоянов", "1999-10-11", "България", "MF", 7, "Активен"),
        (3, "Васил Лечков", "1997-06-06", "България", "FW", 9, "Активен"),
        (3, "Кирил Симов", "1998-03-12", "България", "DF", 2, "Активен"),
        # Club 4 — Лудогорец Разград
        (4, "Владислав Стоянов", "1995-01-18", "България", "GK", 1, "Активен"),
        (4, "Калоян Стоянов", "1998-03-25", "България", "DF", 2, "Активен"),
        (4, "Ивелин Попов", "1996-07-14", "България", "MF", 6, "Активен"),
        (4, "Клавдиу Кейсел", "1997-12-01", "Румъния", "FW", 10, "Активен"),
        (4, "Жуан Пауло", "1999-05-15", "Бразилия", "MF", 8, "Активен"),
        # Club 5 — Черно море Варна
        (5, "Димитър Манолов", "1994-11-22", "България", "GK", 1, "Активен"),
        (5, "Павел Виданов", "1998-01-15", "България", "DF", 4, "Активен"),
        (5, "Атанас Пиров", "1996-09-30", "България", "MF", 8, "Активен"),
        (5, "Иван Стоянов", "1999-05-05", "България", "FW", 11, "Активен"),
        (5, "Мартин Тодоров", "1997-04-22", "България", "DF", 3, "Активен"),
        # Club 6 — Спартак Варна
        (6, "Георги Георгиев", "1995-08-10", "България", "GK", 1, "Активен"),
        (6, "Кристиян Камбулов", "1998-12-03", "България", "DF", 5, "Активен"),
        (6, "Александър Михалков", "1996-02-28", "България", "MF", 7, "Активен"),
        (6, "Борислав Димитров", "1999-07-19", "България", "FW", 10, "Активен"),
        (6, "Добромир Жечев", "1997-11-30", "България", "DF", 2, "Активен"),
        # Club 7 — Локомотив Пловдив
        (7, "Иван Колев", "1994-06-25", "България", "GK", 1, "Активен"),
        (7, "Петър Стайков", "1997-11-14", "България", "DF", 4, "Активен"),
        (7, "Мартин Димитров", "1998-09-30", "България", "MF", 8, "Активен"),
        (7, "Николай Николов", "1996-01-08", "България", "FW", 9, "Активен"),
        (7, "Димитър Димитров", "1999-03-17", "България", "MF", 6, "Активен"),
        # Club 8 — Берое Стара Загора
        (8, "Атанас Атанасов", "1995-10-12", "България", "GK", 1, "Активен"),
        (8, "Иван Иванов", "1998-07-23", "България", "DF", 3, "Активен"),
        (8, "Георги Попов", "1997-02-14", "България", "MF", 7, "Активен"),
        (8, "Кирил Кирилов", "1999-12-01", "България", "FW", 11, "Активен"),
        (8, "Стефан Велев", "1996-04-18", "България", "DF", 5, "Активен"),
        # Club 9 — Славия София
        (9, "Никола Николов", "1993-08-05", "България", "GK", 1, "Активен"),
        (9, "Владимир Иванов", "1996-11-14", "България", "DF", 4, "Активен"),
        (9, "Христо Попов", "1998-03-22", "България", "MF", 10, "Активен"),
        (9, "Денислав Александров", "1997-06-30", "България", "FW", 9, "Активен"),
        (9, "Михаил Петров", "1999-01-12", "България", "DF", 2, "Активен"),
        # Club 10 — Локомотив София
        (10, "Божидар Митрев", "1994-12-18", "България", "GK", 1, "Активен"),
        (10, "Красимир Станоев", "1997-05-09", "България", "DF", 5, "Активен"),
        (10, "Антон Иванов", "1998-08-27", "България", "MF", 8, "Активен"),
        (10, "Спас Георгиев", "1996-02-15", "България", "FW", 11, "Активен"),
        (10, "Валентин Николов", "1995-10-03", "България", "MF", 6, "Активен"),
        # Club 11 — Арда Кърджали
        (11, "Иван Караджов", "1995-07-20", "България", "GK", 1, "Активен"),
        (11, "Пламен Крумов", "1998-04-11", "България", "DF", 4, "Активен"),
        (11, "Станислав Иванов", "1997-09-15", "България", "MF", 7, "Активен"),
        (11, "Тонислав Йорданов", "1999-12-01", "България", "FW", 10, "Активен"),
        (11, "Милчо Ангелов", "1996-03-28", "България", "DF", 2, "Активен"),
        # Club 12 — Ботев Враца
        (12, "Христо Бонев", "1994-06-10", "България", "GK", 1, "Активен"),
        (12, "Валери Домовчийски", "1997-01-25", "България", "DF", 5, "Активен"),
        (12, "Петър Атанасов", "1998-11-05", "България", "MF", 8, "Активен"),
        (12, "Владислав Василев", "1996-08-30", "България", "FW", 9, "Активен"),
        (12, "Красимир Тодоров", "1995-04-17", "България", "MF", 6, "Активен"),
        # Club 13 — Пирин Благоевград
        (13, "Георги Китанов", "1993-12-22", "България", "GK", 1, "Активен"),
        (13, "Иван Бандаловски", "1996-07-14", "България", "DF", 4, "Активен"),
        (13, "Антон Костадинов", "1998-02-18", "България", "MF", 7, "Активен"),
        (13, "Радослав Цонев", "1999-09-28", "България", "FW", 10, "Активен"),
        (13, "Борислав Балджийски", "1997-05-06", "България", "DF", 2, "Активен"),
        # Club 14 — ЦСКА 1948 София
        (14, "Димитър Евтимов", "1995-11-09", "България", "GK", 1, "Активен"),
        (14, "Тодор Неделев", "1998-06-21", "България", "DF", 3, "Активен"),
        (14, "Ивайло Чочев", "1997-03-15", "България", "MF", 8, "Активен"),
        (14, "Кирил Десподов", "1996-10-04", "България", "FW", 11, "Активен"),
        (14, "Георги Йомов", "1999-01-30", "България", "MF", 6, "Активен"),
        # Club 15 — Хебър Пазарджик
        (15, "Илиян Василев", "1994-08-12", "България", "GK", 1, "Активен"),
        (15, "Мартин Кавдански", "1997-11-28", "България", "DF", 5, "Активен"),
        (15, "Стойчо Атанасов", "1998-05-19", "България", "MF", 7, "Активен"),
        (15, "Атанас Илиев", "1996-02-06", "България", "FW", 9, "Активен"),
        (15, "Димитър Велковски", "1995-09-23", "България", "DF", 2, "Активен"),
        # Club 16 — Крумовград
        (16, "Благовест Димов", "1993-04-15", "България", "GK", 1, "Активен"),
        (16, "Йордан Минев", "1997-08-20", "България", "DF", 4, "Активен"),
        (16, "Стефан Янков", "1998-12-03", "България", "MF", 8, "Активен"),
        (16, "Мартин Тошев", "1996-06-17", "България", "FW", 10, "Активен"),
        (16, "Николай Димитров", "1999-03-11", "България", "MF", 6, "Активен"),
        # Club 17 — Етър Велико Търново
        (17, "Ярослав Терзиев", "1995-01-28", "България", "GK", 1, "Активен"),
        (17, "Иван Скерлев", "1998-07-09", "България", "DF", 5, "Активен"),
        (17, "Пламен Иванов", "1997-10-22", "България", "MF", 7, "Активен"),
        (17, "Велислав Василев", "1996-04-14", "България", "FW", 9, "Активен"),
        (17, "Димитър Здравков", "1999-11-02", "България", "DF", 2, "Активен"),
        # Club 18 — Септември София
        (18, "Валентин Галев", "1994-09-05", "България", "GK", 1, "Активен"),
        (18, "Борис Галчев", "1997-12-18", "България", "DF", 4, "Активен"),
        (18, "Кирил Васев", "1998-06-28", "България", "MF", 8, "Активен"),
        (18, "Павел Петков", "1996-03-10", "България", "FW", 11, "Активен"),
        (18, "Светослав Димитров", "1995-08-25", "България", "DF", 2, "Активен"),
    ]
    for player in sample_players:
        cursor.execute(
            "INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            player
        )

    # =============================================
    # 16 Matches (8 existing + 8 new)
    # =============================================
    sample_matches = [
        # Existing — Първа Лига
        (1, 2, 2, 1, '2025-08-01'),
        (1, 3, 0, 0, '2025-08-08'),
        (2, 3, 1, 3, '2025-08-15'),
        (4, 5, 1, 2, '2025-08-02'),
        (6, 7, 0, 1, '2025-08-03'),
        (8, 7, 2, 2, '2025-08-04'),
        (2, 4, 3, 1, '2025-08-05'),
        (3, 5, 1, 1, '2025-08-06'),
        # New — Първа Лига
        (9, 10, 2, 1, '2025-08-10'),
        (1, 9, 3, 0, '2025-08-12'),
        (2, 10, 2, 2, '2025-08-17'),
        (4, 11, 4, 1, '2025-08-19'),
        # New — Втора Лига
        (11, 12, 1, 1, '2025-08-11'),
        (13, 14, 0, 2, '2025-08-18'),
        (15, 16, 1, 1, '2025-08-25'),
        (17, 18, 2, 0, '2025-08-26'),
    ]
    match_ids = []
    for hm, aw, hg, ag, dt in sample_matches:
        cursor.execute(
            "INSERT INTO matches (home_team_id, away_team_id, home_goals, away_goals, match_date, is_played) VALUES (?, ?, ?, ?, ?, 1)",
            (hm, aw, hg, ag, dt)
        )
        match_ids.append(cursor.lastrowid)

    # =============================================
    # Events
    # =============================================
    def _get_player_id(full_name, club_id=None):
        if club_id:
            cursor.execute("SELECT id FROM players WHERE full_name = ? AND club_id = ?", (full_name, club_id))
        else:
            cursor.execute("SELECT id FROM players WHERE full_name = ?", (full_name,))
        row = cursor.fetchone()
        return row[0] if row else None

    m1, m2, m3, m4, m5, m6, m7, m8 = match_ids[:8]
    m9, m10, m11, m12, m13, m14, m15, m16 = match_ids[8:]

    # Existing events
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

    # New events — match 9 (Славия 2-1 Локомотив София)
    pid_hristo = _get_player_id("Христо Попов", 9)
    if pid_hristo:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 34)", (m9, pid_hristo, 9))
    pid_denislav = _get_player_id("Денислав Александров", 9)
    if pid_denislav:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 78)", (m9, pid_denislav, 9))
    pid_spas = _get_player_id("Спас Георгиев", 10)
    if pid_spas:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 61)", (m9, pid_spas, 10))

    # New events — match 10 (Левски 3-0 Славия)
    pid_alex = _get_player_id("Александър Николов", 1)
    if pid_alex:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 15)", (m10, pid_alex, 1))
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 44)", (m10, pid_alex, 1))
    pid_petar = _get_player_id("Петър Петров", 1)
    if pid_petar:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 73)", (m10, pid_petar, 1))

    # New events — match 11 (ЦСКА 2-2 Локомотив София)
    pid_rad = _get_player_id("Радослав Недев", 2)
    if pid_rad:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 22)", (m11, pid_rad, 2))
    pid_georgi_d = _get_player_id("Георги Димитров", 2)
    if pid_georgi_d:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, card_type, minute) VALUES (?, ?, ?, 'yellow', 'Y', 55)", (m11, pid_georgi_d, 2))
    pid_anton = _get_player_id("Антон Иванов", 10)
    if pid_anton:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 30)", (m11, pid_anton, 10))
    pid_valentin = _get_player_id("Валентин Николов", 10)
    if pid_valentin:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 89)", (m11, pid_valentin, 10))

    # New events — match 12 (Лудогорец 4-1 Арда)
    pid_kk = _get_player_id("Клавдиу Кейсел", 4)
    if pid_kk:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 10)", (m12, pid_kk, 4))
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 55)", (m12, pid_kk, 4))
    pid_jp = _get_player_id("Жуан Пауло", 4)
    if pid_jp:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 30)", (m12, pid_jp, 4))
    pid_kalo = _get_player_id("Калоян Стоянов", 4)
    if pid_kalo:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 78)", (m12, pid_kalo, 4))
    pid_toni = _get_player_id("Тонислав Йорданов", 11)
    if pid_toni:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 42)", (m12, pid_toni, 11))

    # New events — match 13 (Арда 1-1 Ботев Враца)
    pid_stan = _get_player_id("Станислав Иванов", 11)
    if pid_stan:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 15)", (m13, pid_stan, 11))
    pid_valeri = _get_player_id("Валери Домовчийски", 12)
    if pid_valeri:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 67)", (m13, pid_valeri, 12))

    # New events — match 14 (Пирин 0-2 ЦСКА 1948)
    pid_kiril_d = _get_player_id("Кирил Десподов", 14)
    if pid_kiril_d:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 23)", (m14, pid_kiril_d, 14))
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 71)", (m14, pid_kiril_d, 14))

    # New events — match 15 (Хебър 1-1 Крумовград)
    pid_atanas = _get_player_id("Атанас Илиев", 15)
    if pid_atanas:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 44)", (m15, pid_atanas, 15))
    pid_martin_t = _get_player_id("Мартин Тошев", 16)
    if pid_martin_t:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 82)", (m15, pid_martin_t, 16))

    # New events — match 16 (Етър 2-0 Септември)
    pid_plamen = _get_player_id("Пламен Иванов", 17)
    if pid_plamen:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 32)", (m16, pid_plamen, 17))
    pid_velislav = _get_player_id("Велислав Василев", 17)
    if pid_velislav:
        cursor.execute("INSERT INTO events (match_id, player_id, club_id, event_type, minute) VALUES (?, ?, ?, 'goal', 67)", (m16, pid_velislav, 17))

    # =============================================
    # Leagues
    # =============================================
    cursor.execute("INSERT INTO leagues (name, season) VALUES ('Първа Лига', '2025')")
    cursor.execute("INSERT INTO leagues (name, season) VALUES ('Втора Лига', '2025')")

    # Първа Лига — clubs 1-10
    for cid in range(1, 11):
        cursor.execute("INSERT INTO league_teams (league_id, club_id) VALUES (1, ?)", (cid,))
    # Втора Лига — clubs 11-18
    for cid in range(11, 19):
        cursor.execute("INSERT INTO league_teams (league_id, club_id) VALUES (2, ?)", (cid,))

    # =============================================
    # Transfers
    # =============================================
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
