from db import fetch_one, fetch_all, execute


def resolve_id(identifier):
    if not identifier:
        return None
    if str(identifier).isdigit():
        lid = int(identifier)
        row = fetch_one("SELECT id FROM leagues WHERE id = ?", (lid,))
        if row:
            return row['id']
    row = fetch_one("SELECT id FROM leagues WHERE LOWER(name) = LOWER(?)", (str(identifier).strip(),))
    if row:
        return row['id']
    return None


def get_by_id(league_id: int):
    return fetch_one("SELECT * FROM leagues WHERE id = ?", (league_id,))


def get_by_name(name: str):
    return fetch_one("SELECT * FROM leagues WHERE LOWER(name) = LOWER(?)", (name.strip(),))


def create(name: str, season: str):
    return execute("INSERT INTO leagues (name, season) VALUES (?, ?)", (name, season))


def get_teams(league_id: int):
    return fetch_all(
        "SELECT c.* FROM clubs c JOIN league_teams lt ON c.id = lt.club_id WHERE lt.league_id = ? ORDER BY c.name",
        (league_id,)
    )


def add_team(league_id: int, club_id: int):
    return execute(
        "INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)",
        (league_id, club_id)
    )
