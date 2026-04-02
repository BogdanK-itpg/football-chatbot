from db import fetch_one, fetch_all, execute
from datetime import datetime, date


def validate_position(position: str) -> bool:
    return position in ['GK', 'DF', 'MF', 'FW']


def validate_number(number) -> bool:
    try:
        num = int(number)
        return 1 <= num <= 99
    except (ValueError, TypeError):
        return False


def validate_birth_date(birth_date: str) -> bool:
    try:
        parsed_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        return parsed_date <= date.today()
    except Exception:
        return False


def get_club_id(club_identifier):
    # Try by name
    if not club_identifier:
        return None
    import re
    # Normalize common leading tokens that may be present from user input
    cid = club_identifier.strip()
    cid = re.sub(r'^(в\s+клуб\s+|в\s+|на\s+клуб\s+|на\s+)', '', cid, flags=re.IGNORECASE).strip()
    # Try exact (case-insensitive) match first using Python casefold for reliable Unicode handling
    try:
        clubs = fetch_all("SELECT id, name FROM clubs")
        if clubs:
            target = cid.casefold()
            for c in clubs:
                if c['name'] and c['name'].casefold() == target:
                    return c['id']
    except Exception:
        pass

    try:
        club_id = int(cid)
        row = fetch_one("SELECT id FROM clubs WHERE id = ?", (club_id,))
        if row:
            return row['id']
    except Exception:
        pass
    # Try fuzzy match (contains) using Python comparison
    try:
        if not locals().get('clubs'):
            clubs = fetch_all("SELECT id, name FROM clubs")
        target = cid.casefold()
        for c in clubs or []:
            if c['name'] and target in c['name'].casefold():
                return c['id']
    except Exception:
        pass

    return None


def get_player_id(player_identifier):
    if not player_identifier:
        return None
    
    player_lower = player_identifier.lower()
    row = fetch_one("SELECT id, full_name FROM players")
    if row:
        if row['full_name'].lower() == player_lower:
            return row['id']
    
    all_players = fetch_all("SELECT id, full_name FROM players")
    for row in all_players:
        if player_lower in row['full_name'].lower():
            return row['id']

    try:
        pid = int(player_identifier)
        row = fetch_one("SELECT id FROM players WHERE id = ?", (pid,))
        if row:
            return row['id']
    except Exception:
        pass

    return None


def add_player(club_id, full_name, birth_date, nationality, position, number, status):
    if not full_name or not full_name.strip():
        return "Името на играча не може да бъде празно."
    if not validate_birth_date(birth_date):
        return "Невaлидна дата на раждане. Използвайте формат YYYY-MM-DD и дата не може да бъде в бъдещето."
    if not nationality or not nationality.strip():
        return "Националността не може да бъде празна."
    if not validate_position(position):
        return "Невaлидна позиция. Използвайте една от: GK, DF, MF, FW."
    if not validate_number(number):
        return "Невaлиден номер. Номерът трябва да бъде между 1 и 99."
    if not status or not status.strip():
        return "Статусът не може да бъде празен."

    club = fetch_one("SELECT id FROM clubs WHERE id = ?", (club_id,))
    if not club:
        return f"Клуб с ID {club_id} не съществува."

    existing = fetch_one(
        "SELECT * FROM players WHERE LOWER(full_name) = LOWER(?) AND club_id = ?",
        (full_name, club_id)
    )
    if existing:
        return f"Играч с име '{full_name}' вече съществува в този клуб."

    res = execute(
        "INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (club_id, full_name, birth_date, nationality, position, int(number), status)
    )
    if res is None:
        return "Грешка при добавяне на играч."
    return f"Играч '{full_name}' беше добавен успешно."


def get_players_by_club(club_identifier=None):
    if club_identifier:
        club_id = get_club_id(club_identifier)
        if not club_id:
            return f"Клуб '{club_identifier}' не съществува."
        rows = fetch_all(
            "SELECT p.*, c.name as club_name FROM players p JOIN clubs c ON p.club_id = c.id WHERE p.club_id = ? ORDER BY p.number",
            (club_id,)
        )
    else:
        rows = fetch_all(
            "SELECT p.*, c.name as club_name FROM players p JOIN clubs c ON p.club_id = c.id ORDER BY c.name, p.number"
        )

    if not rows:
        return "Няма намерени играчи."

    headers = ["ID", "Име", "Клуб", "Поз", "№", "Националност", "Р. Дата", "Статус"]
    col_widths = [4, 22, 24, 5, 4, 15, 12, 10]

    def format_row(row):
        return (
            f"{str(row['id']):<{col_widths[0]}}"
            f"{row['full_name']:<{col_widths[1]}}"
            f"{row['club_name']:<{col_widths[2]}}"
            f"{row['position']:<{col_widths[3]}}"
            f"{str(row['number']):<{col_widths[4]}}"
            f"{row['nationality']:<{col_widths[5]}}"
            f"{str(row['birth_date']):<{col_widths[6]}}"
            f"{row['status']:<{col_widths[7]}}"
        )

    header = "".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-" * sum(col_widths)

    lines = [header, separator]
    for r in rows:
        lines.append(format_row(r))

    return "\n".join(lines)


def update_player_position(player_identifier, new_position):
    if not validate_position(new_position):
        return "Невалидна позиция. Използвайте една от: GK, DF, MF, FW."
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    res = execute("UPDATE players SET position = ? WHERE id = ?", (new_position, pid))
    if res is None:
        return "Грешка при обновяване на позицията."
    return f"Позицията на играч с ID {pid} беше обновена на {new_position}."


def update_player_number(player_identifier, new_number):
    if not validate_number(new_number):
        return "Невалиден номер. Номерът трябва да бъде между 1 и 99."
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    res = execute("UPDATE players SET number = ? WHERE id = ?", (int(new_number), pid))
    if res is None:
        return "Грешка при обновяване на номера."
    return f"Номерът на играч с ID {pid} беше сменен на {new_number}."


def update_player_status(player_identifier, new_status):
    if not new_status or not new_status.strip():
        return "Статусът не може да бъде празен."
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    res = execute("UPDATE players SET status = ? WHERE id = ?", (new_status, pid))
    if res is None:
        return "Грешка при обновяване на статуса."
    return f"Статусът на играч с ID {pid} беше обновен на '{new_status}'."


def delete_player(player_identifier):
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    res = execute("DELETE FROM players WHERE id = ?", (pid,))
    if res is None:
        return "Грешка при изтриване на играча."
    return f"Играч с ID {pid} беше изтрит."
