from repositories import players_repo, clubs_repo
from db import connect, commit, rollback
from utils.logger import log_command


def transfer_player(player_identifier, to_club_identifier):
    pid = players_repo.get_by_name(player_identifier) if not str(player_identifier).isdigit() else players_repo.get_by_id(int(player_identifier))
    if not pid:
        pid = players_repo.get_by_id(int(player_identifier)) if str(player_identifier).isdigit() else players_repo.get_by_name(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."
    pid = pid['id']

    to_cid = None
    if str(to_club_identifier).isdigit():
        club = clubs_repo.get_by_id(int(to_club_identifier))
        if club:
            to_cid = club['id']
    else:
        club = clubs_repo.get_by_name(to_club_identifier)
        if club:
            to_cid = club['id']
    if not to_cid:
        return f"Клуб '{to_club_identifier}' не съществува."

    conn = connect()
    if not conn:
        return "Грешка при свързване с базата данни."

    try:
        p = players_repo.get_club_and_number(pid)
        if not p:
            return f"Играч '{player_identifier}' не съществува."
        if p['club_id'] == to_cid:
            return "Играчът вече е в този клуб."

        conflict = players_repo.check_number_conflict(to_cid, p['number'], pid)
        assigned_number = p['number']
        if conflict:
            used = players_repo.get_used_numbers(to_cid)
            for n in range(1, 100):
                if n not in used:
                    assigned_number = n
                    break

        players_repo.update_club_and_number(pid, to_cid, assigned_number)
        commit(conn)

        if assigned_number != p['number']:
            result = f"Играч '{p['full_name']}' беше трансфериран в клуб с ID {to_cid}. Присвоен нов номер: #{assigned_number}."
        else:
            result = f"Играч '{p['full_name']}' беше трансфериран в клуб с ID {to_cid}."
        try:
            log_command(f"transfer {player_identifier} -> {to_club_identifier}", result)
        except Exception:
            pass
        return result

    except Exception:
        rollback(conn)
        return "Грешка при трансфер на играча."
    finally:
        try:
            conn.close()
        except Exception:
            pass
