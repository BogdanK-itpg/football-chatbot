from db import connect, commit, rollback
from services.players_service import get_player_id, get_club_id
from utils.logger import log_command


def transfer_player(player_identifier, to_club_identifier):
    """Transfer a player to another club inside a DB transaction.

    Returns a success message or an error message string on failure.
    """
    pid = get_player_id(player_identifier)
    if not pid:
        return f"Играч '{player_identifier}' не съществува."

    to_cid = get_club_id(to_club_identifier)
    if not to_cid:
        return f"Клуб '{to_club_identifier}' не съществува."

    conn = connect()
    if not conn:
        return "Грешка при свързване с базата данни."

    try:
        cur = conn.cursor()

        # fetch current player info inside the transaction
        cur.execute("SELECT club_id, number, full_name FROM players WHERE id = ?", (pid,))
        p = cur.fetchone()
        if not p:
            return f"Играч '{player_identifier}' не съществува."

        if p['club_id'] == to_cid:
            return "Играчът вече е в този клуб."

        # check if jersey number is taken in target club
        cur.execute("SELECT id FROM players WHERE club_id = ? AND number = ? AND id != ?", (to_cid, p['number'], pid))
        conflict = cur.fetchone()
        assigned_number = p['number']
        if conflict:
            # find smallest available number in target club
            cur.execute("SELECT number FROM players WHERE club_id = ? ORDER BY number", (to_cid,))
            used = {r['number'] for r in cur.fetchall()}
            for n in range(1, 100):
                if n not in used:
                    assigned_number = n
                    break

        # perform transfer (and possibly assign new number)
        cur.execute("UPDATE players SET club_id = ?, number = ? WHERE id = ?", (to_cid, assigned_number, pid))
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
