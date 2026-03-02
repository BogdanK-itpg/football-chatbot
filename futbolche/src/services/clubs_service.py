from db import fetch_one, fetch_all, execute


def _normalize_name(name: str) -> str:
    return name.strip()


def create_club(name: str, city: str = 'Unknown', founded_year: int = None) -> str:
    """Create a new club with validation.

    Returns a user-friendly message.
    """
    if not name or not name.strip():
        return "Името не може да бъде празно."

    name = _normalize_name(name)

    # Check duplicate (case-insensitive)
    existing = fetch_one("SELECT id FROM clubs WHERE LOWER(name) = LOWER(?)", (name,))
    if existing:
        return "Клуб с това име вече съществува."

    try:
        try:
            founded = int(founded_year) if founded_year else 1900
        except (ValueError, TypeError):
            founded = 1900

        res = execute(
            "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
            (name, city, founded)
        )

        if res is None:
            return "Грешка при добавяне на клуба."
        return f"Клуб '{name}' беше добавен успешно."
    except Exception:
        return "Грешка при добавяне на клуба."


def list_clubs() -> str:
    """Return a human readable list of clubs."""
    try:
        rows = fetch_all("SELECT id, name, city, founded_year FROM clubs ORDER BY id")
    except Exception:
        return "Няма добавени клубове."

    if not rows:
        return "Няма добавени клубове."

    lines = []
    for idx, r in enumerate(rows, start=1):
        lines.append(f"{idx}. {r['name']}")
    return "\n".join(lines)


def update_club(identifier, new_name: str = None, new_city: str = None, new_founded_year: int = None) -> str:
    """Update club by id or name. Returns message."""
    # Resolve identifier to id
    club = None
    if isinstance(identifier, int) or str(identifier).isdigit():
        club = fetch_one("SELECT * FROM clubs WHERE id = ?", (int(identifier),))
    else:
        club = fetch_one("SELECT * FROM clubs WHERE LOWER(name) = LOWER(?)", (str(identifier),))

    if not club:
        return "Клубът не беше намерен."

    updates = []
    params = []
    if new_name:
        updates.append("name = ?")
        params.append(new_name.strip())
    if new_city:
        updates.append("city = ?")
        params.append(new_city.strip())
    if new_founded_year:
        try:
            params.append(int(new_founded_year))
            updates.append("founded_year = ?")
        except (ValueError, TypeError):
            return "Невалидна година на основаване."

    if not updates:
        return "Няма зададени промени."

    params.append(club['id'])
    sql = f"UPDATE clubs SET {', '.join(updates)} WHERE id = ?"
    res = execute(sql, tuple(params))
    if res is None:
        return "Грешка при обновяване на клуба."
    return "Клубът беше успешно обновен."


def delete_club(identifier) -> str:
    """Delete club by id or name."""
    # Resolve
    club = None
    if isinstance(identifier, int) or str(identifier).isdigit():
        club = fetch_one("SELECT id, name FROM clubs WHERE id = ?", (int(identifier),))
    else:
        club = fetch_one("SELECT id, name FROM clubs WHERE LOWER(name) = LOWER(?)", (str(identifier),))

    if not club:
        return "Няма такъв клуб."

    try:
        res = execute("DELETE FROM clubs WHERE id = ?", (club['id'],))
        if res is None:
            return "Грешка при изтриване на клуба."
        return f"Клуб '{club['name']}' беше изтрит."
    except Exception:
        return "Грешка при изтриване на клуба."
