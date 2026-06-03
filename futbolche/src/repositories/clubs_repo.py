from db import fetch_one, fetch_all, execute


def get_by_id(club_id: int):
    return fetch_one("SELECT id, name, city, founded_year FROM clubs WHERE id = ?", (club_id,))


def get_by_name(name: str):
    row = fetch_one("SELECT id, name, city, founded_year FROM clubs WHERE LOWER(name) = LOWER(?)", (name.strip(),))
    if row:
        return row
    rows = fetch_all("SELECT id, name, city, founded_year FROM clubs")
    target = name.strip().casefold()
    for r in rows:
        if target in r['name'].casefold():
            return r
    return None


def get_all():
    return fetch_all("SELECT id, name, city, founded_year FROM clubs ORDER BY id")


def create(name: str, city: str = 'Unknown', founded_year: int = 1900):
    return execute(
        "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
        (name.strip(), city, founded_year)
    )


def update(club_id: int, **kwargs):
    allowed = {'name', 'city', 'founded_year'}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return None
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    params = list(updates.values()) + [club_id]
    return execute(f"UPDATE clubs SET {set_clause} WHERE id = ?", tuple(params))


def delete(club_id: int):
    return execute("DELETE FROM clubs WHERE id = ?", (club_id,))


def exists(club_id: int) -> bool:
    row = fetch_one("SELECT 1 FROM clubs WHERE id = ?", (club_id,))
    return row is not None
