"""Validation functions for match events and transfers."""

from repositories import matches_repo, players_repo, events_repo, clubs_repo, transfers_repo


def validate_minute(minute_str) -> tuple:
    """Returns (is_valid: bool, error_message: str)."""
    if minute_str is None:
        return False, "Минутата е задължителна."
    try:
        minute = int(minute_str)
    except (ValueError, TypeError):
        return False, "Минутата трябва да бъде цяло число."
    if minute < 1 or minute > 120:
        return False, "Минутата трябва да бъде между 1 и 120."
    return True, ""


def validate_score(home_goals_str, away_goals_str) -> tuple:
    """Returns (is_valid: bool, error_message: str)."""
    if home_goals_str is None or away_goals_str is None:
        return False, "Резултатът е задължителен."
    try:
        hg = int(home_goals_str)
        ag = int(away_goals_str)
    except (ValueError, TypeError):
        return False, "Резултатът трябва да бъде две цели числа (напр. 2:1)."
    if hg < 0 or ag < 0:
        return False, "Головете не могат да бъдат отрицателни числа."
    return True, ""


def validate_player_in_match(player_id: int, match_id: int) -> tuple:
    """Check that the player's club is one of the two teams in the match."""
    match = matches_repo.get_by_id(match_id)
    if not match:
        return False, "Мачът не съществува."
    player_club_id = players_repo.get_club_id(player_id)
    if player_club_id is None:
        return False, "Играчът не съществува."
    if player_club_id != match['home_team_id'] and player_club_id != match['away_team_id']:
        return False, "Играчът не участва в този мач (неговият отбор не играе в мача)."
    return True, ""


def validate_no_duplicate_result(match_id: int) -> tuple:
    """Reject if match already has a result."""
    if matches_repo.is_played(match_id):
        return False, "Мачът вече има записан резултат. Не можете да го запишете отново."
    return True, ""


def validate_no_goal_after_red(player_id: int, match_id: int) -> tuple:
    """Reject goal if player already has a red card in this match."""
    if events_repo.has_red_in_match(match_id, player_id):
        return False, "Играчът е получил червен картон и не може да отбележи гол."
    return True, ""


def validate_card_allowed(player_id: int, match_id: int, card_type: str) -> tuple:
    """Validate card rules."""
    cards = events_repo.count_cards_in_match(match_id, player_id)
    if cards['red'] >= 1:
        return False, "Играчът вече е получил червен картон."
    if card_type == 'Y' and cards['yellow'] >= 1:
        return False, "Играчът вече има жълт картон. Втори жълт = червен картон. Използвайте 'R'."
    if card_type == 'R' and cards['yellow'] >= 1:
        return True, ""  # Second yellow converted to red is valid
    return True, ""


def validate_transfer_date(date_str: str) -> tuple:
    """Returns (is_valid: bool, error_message: str)."""
    if not date_str:
        return False, "Датата на трансфер е задължителна."
    try:
        from datetime import datetime
        parsed = datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        return True, ""
    except ValueError:
        return False, "Невалидна дата. Използвайте формат YYYY-MM-DD."


def validate_transfer_fee(fee) -> tuple:
    """Returns (is_valid: bool, error_message: str)."""
    if fee is None or fee == '':
        return True, ""
    try:
        val = float(fee)
        if val < 0:
            return False, "Таксата не може да бъде отрицателна."
        return True, ""
    except (ValueError, TypeError):
        return False, "Невалидна сума. Таксата трябва да бъде число."


def validate_from_club(player_club_id, from_club_identifier: str) -> tuple:
    """Returns (is_valid: bool, error_message: str).
    Checks that the player's current club matches the claimed from_club.
    Handles free agent keywords when player_club_id is None.
    """
    FREE_AGENT_KEYWORDS = {"none", "free", "няма", "свободен", "без клуб"}
    is_free_agent_claim = from_club_identifier is None or str(from_club_identifier).strip().lower() in FREE_AGENT_KEYWORDS

    if player_club_id is None:
        if not is_free_agent_claim:
            return False, "Играчът е свободен агент. Посочете 'няма' или 'free' като текущ клуб."
        return True, ""
    else:
        if is_free_agent_claim:
            return False, "Играчът не е свободен агент. Посочете правилния текущ клуб."
        if str(from_club_identifier).isdigit():
            club = clubs_repo.get_by_id(int(from_club_identifier))
        else:
            club = clubs_repo.get_by_name(from_club_identifier)
        if not club:
            return False, "Клубът не съществува."
        if player_club_id != club['id']:
            return False, "Играчът не играе в посочения клуб."
        return True, ""


def validate_player_belongs_to_club(player_id: int, club_identifier: str) -> tuple:
    """Check that the player belongs to the specified club."""
    club = clubs_repo.get_by_name(club_identifier) if not club_identifier.isdigit() else clubs_repo.get_by_id(int(club_identifier))
    if not club:
        return False, "Клубът не съществува."
    player_club_id = players_repo.get_club_id(player_id)
    if player_club_id is None:
        return False, "Играчът не съществува."
    if player_club_id != club['id']:
        return False, "Играчът не принадлежи към този клуб."
    return True, ""
