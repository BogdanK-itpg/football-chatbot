from db import fetch_one, fetch_all, execute


def get_by_id(player_id: int):
    return fetch_one(
        "SELECT p.*, c.name as club_name FROM players p LEFT JOIN clubs c ON p.club_id = c.id WHERE p.id = ?",
        (player_id,)
    )


def get_by_name(name: str):
    row = fetch_one("SELECT id, full_name, club_id FROM players WHERE LOWER(full_name) = LOWER(?)", (name.strip(),))
    if row:
        return row
    rows = fetch_all("SELECT id, full_name, club_id FROM players")
    target = name.strip().casefold()
    for r in rows:
        if target in r['full_name'].casefold():
            return r
    return None


def get_by_club(club_id: int):
    return fetch_all(
        "SELECT p.*, c.name as club_name FROM players p LEFT JOIN clubs c ON p.club_id = c.id WHERE p.club_id = ? ORDER BY p.number",
        (club_id,)
    )


def get_all():
    return fetch_all(
        "SELECT p.*, c.name as club_name FROM players p LEFT JOIN clubs c ON p.club_id = c.id ORDER BY c.name, p.number"
    )


def create(club_id: int, full_name: str, birth_date: str, nationality: str, position: str, number: int, status: str):
    return execute(
        "INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (club_id, full_name.strip(), birth_date, nationality.strip(), position, number, status.strip())
    )


def update(player_id: int, **kwargs):
    allowed = {'position', 'number', 'status', 'club_id', 'full_name'}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return None
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    params = list(updates.values()) + [player_id]
    return execute(f"UPDATE players SET {set_clause} WHERE id = ?", tuple(params))


def delete(player_id: int):
    return execute("DELETE FROM players WHERE id = ?", (player_id,))


def get_club_id(player_id: int):
    row = fetch_one("SELECT club_id FROM players WHERE id = ?", (player_id,))
    return row['club_id'] if row else None


def exists(player_id: int) -> bool:
    row = fetch_one("SELECT 1 FROM players WHERE id = ?", (player_id,))
    return row is not None


def get_club_and_number(player_id: int):
    """Get club_id, number, full_name for a player."""
    return fetch_one(
        "SELECT club_id, number, full_name FROM players WHERE id = ?",
        (player_id,)
    )


def check_number_conflict(club_id: int, number: int, exclude_player_id: int):
    """Check if another player in the club has the same number."""
    return fetch_one(
        "SELECT id FROM players WHERE club_id = ? AND number = ? AND id != ?",
        (club_id, number, exclude_player_id)
    )


def get_used_numbers(club_id: int):
    """Get all shirt numbers used in a club."""
    rows = fetch_all(
        "SELECT number FROM players WHERE club_id = ? ORDER BY number",
        (club_id,)
    )
    return {r['number'] for r in rows}


def update_club_and_number(player_id: int, club_id: int, number: int, conn=None):
    """Update a player's club and shirt number."""
    return execute(
        "UPDATE players SET club_id = ?, number = ? WHERE id = ?",
        (club_id, number, player_id),
        conn=conn
    )


def exists_by_name_club(full_name: str, club_id: int) -> bool:
    row = fetch_one(
        "SELECT 1 FROM players WHERE LOWER(full_name) = LOWER(?) AND club_id = ?",
        (full_name.strip(), club_id)
    )
    return row is not None
