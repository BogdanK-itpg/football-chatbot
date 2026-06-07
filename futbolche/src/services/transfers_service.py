from datetime import datetime, date
from repositories import players_repo, clubs_repo, transfers_repo
from db import connect, commit, rollback
from utils.logger import log_command

FREE_AGENT_KEYWORDS = {"none", "free", "няма", "свободен", "без клуб"}


def _resolve_player(player_identifier):
    pid = None
    if str(player_identifier).isdigit():
        p = players_repo.get_by_id(int(player_identifier))
        if p:
            pid = p['id']
    if not pid:
        p = players_repo.get_by_name(player_identifier)
        if p:
            pid = p['id']
    return pid


def _resolve_club(club_identifier):
    if not club_identifier:
        return None
    if str(club_identifier).isdigit():
        club = clubs_repo.get_by_id(int(club_identifier))
        if club:
            return club['id']
    club = clubs_repo.get_by_name(club_identifier)
    return club['id'] if club else None


def _validate_transfer_date(date_str):
    if not date_str:
        return date.today().isoformat(), None
    try:
        parsed = datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        return parsed.isoformat(), None
    except ValueError:
        return None, "Невалидна дата. Използвайте формат YYYY-MM-DD."


def _validate_fee(fee_str):
    if fee_str is None or fee_str == '':
        return None, None
    try:
        val = float(fee_str)
        if val < 0:
            return None, "Таксата не може да бъде отрицателна."
        return val, None
    except (ValueError, TypeError):
        return None, "Невалидна сума. Таксата трябва да бъде число."


def _is_free_agent(club_identifier):
    if club_identifier is None:
        return True
    return str(club_identifier).strip().lower() in FREE_AGENT_KEYWORDS


def transfer_player(player_identifier, to_club_identifier, from_club_identifier=None, transfer_date=None, fee=None, note=None):
    pid = _resolve_player(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."

    to_cid = _resolve_club(to_club_identifier)
    if not to_cid:
        return f"Клуб '{to_club_identifier}' не съществува."

    date_str, date_err = _validate_transfer_date(transfer_date)
    if date_err:
        return date_err

    fee_val, fee_err = _validate_fee(fee)
    if fee_err:
        return fee_err

    p = players_repo.get_club_and_number(pid)
    if not p:
        return f"Играч '{player_identifier}' не съществува."

    if p['club_id'] == to_cid:
        return "Играчът вече е в този клуб."

    from_cid = None
    if from_club_identifier is not None and not _is_free_agent(from_club_identifier):
        from_cid = _resolve_club(from_club_identifier)
        if not from_cid:
            return f"Клуб '{from_club_identifier}' не съществува."

    if p['club_id'] is None:
        if not _is_free_agent(from_club_identifier):
            return "Играчът е свободен агент. Посочете 'няма' или 'free' като текущ клуб."
    else:
        if _is_free_agent(from_club_identifier):
            return "Играчът не е свободен агент. Посочете правилния текущ клуб."
        if from_cid is not None and p['club_id'] != from_cid:
            return "Играчът не играе в посочения клуб."

    conflict = players_repo.check_number_conflict(to_cid, p['number'], pid)
    assigned_number = p['number']
    if conflict:
        used = players_repo.get_used_numbers(to_cid)
        for n in range(1, 100):
            if n not in used:
                assigned_number = n
                break

    conn = connect()
    if not conn:
        return "Грешка при свързване с базата данни."

    try:
        players_repo.update_club_and_number(pid, to_cid, assigned_number, conn=conn)
        transfers_repo.create(pid, p['club_id'], to_cid, date_str, fee_val, note, conn=conn)
        commit(conn)

        if assigned_number != p['number']:
            result = f"Играч '{p['full_name']}' беше трансфериран в клуб '{to_club_identifier}'. Присвоен нов номер: #{assigned_number}."
        else:
            result = f"Играч '{p['full_name']}' беше трансфериран в клуб '{to_club_identifier}'."

        log_command(f"трансфер {player_identifier} от {from_club_identifier} в {to_club_identifier}", "transfer_player", "OK", result, {"player": pid, "to_club": to_cid})
        return result

    except Exception as e:
        rollback(conn)
        log_command(f"трансфер {player_identifier} от {from_club_identifier} в {to_club_identifier}", "transfer_player", "ERROR", str(e), {"player": pid, "to_club": to_cid})
        return "Грешка при трансфер на играча."
    finally:
        try:
            conn.close()
        except Exception:
            pass


def list_transfers_by_player(player_identifier):
    pid = _resolve_player(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."

    rows = transfers_repo.get_by_player(pid)
    if not rows:
        return f"Няма трансфери за играч '{player_identifier}'."

    lines = [f"Трансфери на {rows[0]['player_name'] if 'player_name' in rows[0] else player_identifier}:"]
    for r in rows:
        from_name = r['from_club_name'] if r['from_club_name'] else "свободен агент"
        fee_str = f", такса: {r['fee']:.2f}" if r['fee'] is not None else ""
        lines.append(f"  {r['transfer_date']}: {from_name} → {r['to_club_name']}{fee_str}")
    return "\n".join(lines)


def list_transfers_by_club(club_identifier):
    cid = _resolve_club(club_identifier)
    if not cid:
        return f"Клуб '{club_identifier}' не съществува."

    rows = transfers_repo.get_by_club(cid)
    if not rows:
        return f"Няма трансфери за клуб '{club_identifier}'."

    lines = [f"Трансфери на клуб '{club_identifier}':"]
    for r in rows:
        from_name = r['from_club_name'] if r['from_club_name'] else "свободен агент"
        fee_str = f", такса: {r['fee']:.2f}" if r['fee'] is not None else ""
        if r['from_club_id'] == cid:
            lines.append(f"  {r['transfer_date']}: {r['player_name']} {from_name} → {r['to_club_name']} (напуска){fee_str}")
        else:
            lines.append(f"  {r['transfer_date']}: {r['player_name']} {from_name} → {r['to_club_name']} (пристига){fee_str}")
    return "\n".join(lines)
