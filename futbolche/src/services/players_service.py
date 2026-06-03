from datetime import datetime, date
from repositories import players_repo, clubs_repo


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
    if not club_identifier:
        return None
    cid = club_identifier.strip()
    if cid.isdigit():
        club = clubs_repo.get_by_id(int(cid))
        if club:
            return club['id']
    club = clubs_repo.get_by_name(cid)
    return club['id'] if club else None


def get_player_id(player_identifier):
    if not player_identifier:
        return None
    if str(player_identifier).isdigit():
        p = players_repo.get_by_id(int(player_identifier))
        if p:
            return p['id']
    p = players_repo.get_by_name(player_identifier)
    return p['id'] if p else None


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
    if not clubs_repo.exists(club_id):
        return f"Клуб с ID {club_id} не съществува."
    if players_repo.exists_by_name_club(full_name, club_id):
        return f"Играч с име '{full_name}' вече съществува в този клуб."
    res = players_repo.create(club_id, full_name, birth_date, nationality, position, int(number), status)
    if res is None:
        return "Грешка при добавяне на играч."
    return f"Играч '{full_name}' беше добавен успешно."


def get_players_by_club(club_identifier=None):
    if club_identifier:
        club_id = get_club_id(club_identifier)
        if not club_id:
            return f"Клуб '{club_identifier}' не съществува."
        rows = players_repo.get_by_club(club_id)
    else:
        rows = players_repo.get_all()
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
    res = players_repo.update(pid, position=new_position)
    if res is None:
        return "Грешка при обновяване на позицията."
    return f"Позицията на играч с ID {pid} беше обновена на {new_position}."


def update_player_number(player_identifier, new_number):
    if not validate_number(new_number):
        return "Невалиден номер. Номерът трябва да бъде между 1 и 99."
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    res = players_repo.update(pid, number=int(new_number))
    if res is None:
        return "Грешка при обновяване на номера."
    return f"Номерът на играч с ID {pid} беше сменен на {new_number}."


def update_player_status(player_identifier, new_status):
    if not new_status or not new_status.strip():
        return "Статусът не може да бъде празен."
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    res = players_repo.update(pid, status=new_status.strip())
    if res is None:
        return "Грешка при обновяване на статуса."
    return f"Статусът на играч с ID {pid} беше обновен на '{new_status}'."


def delete_player(player_identifier):
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    res = players_repo.delete(pid)
    if res is None:
        return "Грешка при изтриване на играча."
    return f"Играч с ID {pid} беше изтрит."
