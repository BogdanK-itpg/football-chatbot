"""Handlers for the 6 Bulgarian match commands."""

import services.matches_service as matches
import services.players_service as players
from repositories import matches_repo, clubs_repo, players_repo, events_repo, leagues_repo
from validators import (
    validate_minute, validate_score, validate_player_in_match,
    validate_no_duplicate_result, validate_no_goal_after_red,
    validate_card_allowed, validate_player_belongs_to_club
)
from state import set_current_match, get_current_match, clear_current_match


# ---------------------------------------------------------------------------
# Handler A: Покажи кръг <N> <лига> <сезон>
# ---------------------------------------------------------------------------
def handle_show_round(params):
    """Show all matches for a given round in a league."""
    round_no = params.get('round_no')
    league_name = params.get('league_name') or params.get('league_identifier')
    season = params.get('season')

    if not round_no or not league_name:
        return "Формат: покажи кръг [номер] [лига] [сезон]"

    try:
        round_no = int(round_no)
    except (ValueError, TypeError):
        return "Номерът на кръга трябва да бъде цяло число."

    lid = leagues_repo.resolve_id(league_name)
    if not lid:
        return f"Лига '{league_name}' не съществува."

    rows = matches_repo.get_by_league(lid, round_no)
    if not rows:
        return f"Няма мачове за кръг {round_no} в лига '{league_name}'."

    out = [f"--- Кръг {round_no} ---"]
    for r in rows:
        hg = r['home_goals'] if r['home_goals'] is not None else '-'
        ag = r['away_goals'] if r['away_goals'] is not None else '-'
        status = "ИЗИГРАН" if r['is_played'] else "ПРЕДСТОЯЩ"
        out.append(
            f"ID:{r['id']} | {r['match_date']} | "
            f"{r['home_name']} {hg}:{ag} {r['away_name']} | {status}"
        )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Handler B: Резултат <Домакин>-<Гост> <X>:<Y> запиши
# ---------------------------------------------------------------------------
def handle_save_result(params):
    """Save final result for an existing match."""
    home_team = params.get('home_team')
    away_team = params.get('away_team')
    home_goals = params.get('home_goals')
    away_goals = params.get('away_goals')

    if not all([home_team, away_team, home_goals is not None, away_goals is not None]):
        return "Формат: резултат [домакин]-[гост] [домакин_голове]:[гост_голове] запиши"

    # Validate score
    valid, err = validate_score(home_goals, away_goals)
    if not valid:
        return err

    # Resolve clubs
    home_club = clubs_repo.get_by_name(home_team) if not home_team.isdigit() else clubs_repo.get_by_id(int(home_team))
    away_club = clubs_repo.get_by_name(away_team) if not away_team.isdigit() else clubs_repo.get_by_id(int(away_team))
    if not home_club:
        return f"Клуб '{home_team}' не съществува."
    if not away_club:
        return f"Клуб '{away_team}' не съществува."

    # Find the match — use current match from state, or find by teams
    match_id = get_current_match()
    if match_id:
        match = matches_repo.get_by_id(match_id)
        if not match:
            return "Избраният мач не е намерен."
        if match['home_team_id'] != home_club['id'] or match['away_team_id'] != away_club['id']:
            return "Избраният мач не съответства на посочените отбори."
    else:
        # Try to find the match by teams (most recent unplayed)
        all_m = matches_repo.get_all()
        match = None
        for m in all_m:
            if (m['home_team_id'] == home_club['id'] and m['away_team_id'] == away_club['id']) \
               and not m['is_played']:
                match = m
                break
        if not match:
            return "Няма намерен неплаиран мач между тези отбори. Използвайте 'избери мач [ID]' първо."

    # Prevent duplicate
    valid, err = validate_no_duplicate_result(match['id'])
    if not valid:
        return err

    # Save result
    res = matches_repo.set_score(match['id'], int(home_goals), int(away_goals))
    if res is None:
        return "Грешка при запис на резултата."

    return (f"Резултатът {int(home_goals)}:{int(away_goals)} за мач "
            f"{match['id']} ({match['home_name']} vs {match['away_name']}) беше записан успешно.")


# ---------------------------------------------------------------------------
# Handler C: Гол <Играч> <Отбор> <минута> минута
# ---------------------------------------------------------------------------
def handle_add_goal(params):
    """Add a goal event for a player."""
    player_name = params.get('player_name') or params.get('player_identifier')
    team_name = params.get('team_name') or params.get('club_identifier')
    minute = params.get('minute')

    if not player_name or not team_name or minute is None:
        return "Формат: гол [играч] [отбор] [минута] минута"

    # Validate minute
    valid, err = validate_minute(minute)
    if not valid:
        return err

    # Resolve player
    pid = players.get_player_id(player_name)
    if not pid:
        return f"Играч '{player_name}' не съществува."

    # Validate player belongs to team
    valid, err = validate_player_belongs_to_club(pid, team_name)
    if not valid:
        return err

    # Resolve team
    club = clubs_repo.get_by_name(team_name)
    if not club:
        return f"Клуб '{team_name}' не съществува."

    # Get match — from state or fail
    match_id = get_current_match()
    if not match_id:
        return "Няма избран мач. Използвайте 'избери мач [ID]' първо."

    # Validate player participates in match
    valid, err = validate_player_in_match(pid, match_id)
    if not valid:
        return err

    # Reject if match already played
    if matches_repo.is_played(match_id):
        return "Мачът вече е приключил. Не можете да добавяте голове след като резултатът е записан."

    # Reject goal after red card
    valid, err = validate_no_goal_after_red(pid, match_id)
    if not valid:
        return err

    # Record the event
    result = matches.record_event(match_id, pid, club['id'], 'goal', minute=int(minute))
    if "успешно" not in result.lower():
        return result

    # Update match score
    match = matches_repo.get_by_id(match_id)
    if match:
        is_home = (club['id'] == match['home_team_id'])
        matches_repo.increment_score(match_id, is_home)

    return f"Гол за {player_name} в {minute}' минута — записан успешно."


# ---------------------------------------------------------------------------
# Handler D: Избери мач <match_id>
# ---------------------------------------------------------------------------
def handle_select_match(params):
    """Select a match as the current context."""
    match_id = params.get('match_id')
    if not match_id:
        return "Формат: избери мач [ID]"
    try:
        match_id = int(match_id)
    except (ValueError, TypeError):
        return "ID на мача трябва да бъде цяло число."
    if not matches_repo.exists(match_id):
        return f"Мач с ID {match_id} не съществува."
    set_current_match(match_id)
    match = matches_repo.get_by_id(match_id)
    return (f"Избран мач ID {match_id}: {match['home_name']} vs {match['away_name']} "
            f"({match['match_date']}).")


# ---------------------------------------------------------------------------
# Handler E: Картон <Играч> <Отбор> <Y/R> <минута>
# ---------------------------------------------------------------------------
def handle_add_card(params):
    """Add a card event for a player."""
    player_name = params.get('player_name') or params.get('player_identifier')
    team_name = params.get('team_name') or params.get('club_identifier')
    card_type = params.get('card_type')
    minute = params.get('minute')

    if not player_name or not team_name or not card_type or minute is None:
        return "Формат: картон [играч] [отбор] [Y/R] [минута]"

    card_type = card_type.upper()
    if card_type not in ('Y', 'R'):
        return "Типът картон трябва да бъде Y (жълт) или R (червен)."

    # Validate minute
    valid, err = validate_minute(minute)
    if not valid:
        return err

    # Resolve player
    pid = players.get_player_id(player_name)
    if not pid:
        return f"Играч '{player_name}' не съществува."

    # Validate player belongs to team
    valid, err = validate_player_belongs_to_club(pid, team_name)
    if not valid:
        return err

    # Resolve team
    club = clubs_repo.get_by_name(team_name)
    if not club:
        return f"Клуб '{team_name}' не съществува."

    # Get match
    match_id = get_current_match()
    if not match_id:
        return "Няма избран мач. Използвайте 'избери мач [ID]' първо."

    # Validate player in match
    valid, err = validate_player_in_match(pid, match_id)
    if not valid:
        return err

    # Advanced card rules
    valid, err = validate_card_allowed(pid, match_id, card_type)
    if not valid:
        return err

    # Convert second yellow to red
    event_type = 'red' if card_type == 'R' else 'yellow'
    actual_card_type = card_type

    # Check if this is a second yellow that should be a red
    if card_type == 'Y':
        existing = events_repo.count_cards_in_match(match_id, pid)
        if existing['yellow'] >= 1:
            # Auto-convert to red
            event_type = 'red'
            actual_card_type = 'R'

    # Record the event
    result = matches.record_event(match_id, pid, club['id'], event_type,
                                  minute=int(minute), card_type=actual_card_type)
    return result


# ---------------------------------------------------------------------------
# Handler F: Покажи събития or Покажи събития <match_id>
# ---------------------------------------------------------------------------
def handle_show_events(params):
    """Show all events for a match."""
    match_id = params.get('match_id')
    if not match_id:
        match_id = get_current_match()
    if not match_id:
        return "Няма избран мач. Използвайте 'покажи събития [ID]' или 'избери мач [ID]' първо."
    try:
        match_id = int(match_id)
    except (ValueError, TypeError):
        return "ID на мача трябва да бъде цяло число."
    return matches.get_match_events(match_id)
