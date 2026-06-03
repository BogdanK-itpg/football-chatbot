from db import fetch_one, fetch_all, execute


def get_by_match(match_id: int):
    return fetch_all(
        """SELECT e.*, p.full_name as player_name
           FROM events e
           LEFT JOIN players p ON e.player_id = p.id
           WHERE e.match_id = ?
           ORDER BY COALESCE(e.minute, 0)""",
        (match_id,)
    )


def create(match_id: int, player_id: int, club_id: int, event_type: str,
           minute=None, card_type=None, is_own_goal=0):
    return execute(
        "INSERT INTO events (match_id, player_id, club_id, event_type, minute, card_type, is_own_goal) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (match_id, player_id, club_id, event_type, minute, card_type, is_own_goal)
    )


def count_by_type(match_id: int, player_id: int, event_type: str) -> int:
    row = fetch_one(
        "SELECT COUNT(*) as cnt FROM events WHERE match_id = ? AND player_id = ? AND event_type = ?",
        (match_id, player_id, event_type)
    )
    return row['cnt'] if row else 0


def count_cards_in_match(match_id: int, player_id: int) -> dict:
    """Return dict with 'yellow' and 'red' counts for a player in a match."""
    yellows = fetch_one(
        "SELECT COUNT(*) as cnt FROM events WHERE match_id = ? AND player_id = ? AND event_type = 'yellow'",
        (match_id, player_id)
    )
    reds = fetch_one(
        "SELECT COUNT(*) as cnt FROM events WHERE match_id = ? AND player_id = ? AND event_type = 'red'",
        (match_id, player_id)
    )
    return {
        'yellow': yellows['cnt'] if yellows else 0,
        'red': reds['cnt'] if reds else 0,
    }


def has_red_in_match(match_id: int, player_id: int) -> bool:
    row = fetch_one(
        "SELECT 1 FROM events WHERE match_id = ? AND player_id = ? AND event_type = 'red'",
        (match_id, player_id)
    )
    return row is not None


def count_by_player(player_id: int, event_type: str) -> int:
    """Count events of a type for a player across all matches."""
    row = fetch_one(
        "SELECT COUNT(*) as cnt FROM events WHERE player_id = ? AND event_type = ?",
        (player_id, event_type)
    )
    return row['cnt'] if row else 0


def get_last_event_before_minute(match_id: int, player_id: int, minute: int):
    """Get the most recent event for a player in a match before a given minute."""
    return fetch_one(
        "SELECT * FROM events WHERE match_id = ? AND player_id = ? AND minute < ? ORDER BY minute DESC LIMIT 1",
        (match_id, player_id, minute)
    )
