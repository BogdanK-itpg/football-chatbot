"""Handlers for match commands — thin wrappers over matches_service."""

import services.matches_service as matches
from state import get_current_match


# ---------------------------------------------------------------------------
# Handler A: Покажи кръг <N> <лига> <сезон>
# ---------------------------------------------------------------------------
def handle_show_round(params):
    round_no = params.get('round_no')
    league_name = params.get('league_name') or params.get('league_identifier')
    if not round_no or not league_name:
        return "Формат: покажи кръг [номер] [лига] [сезон]"
    return matches.show_round(round_no, league_name)


# ---------------------------------------------------------------------------
# Handler B: Резултат <Домакин>-<Гост> <X>:<Y> запиши
# ---------------------------------------------------------------------------
def handle_save_result(params):
    home_team = params.get('home_team')
    away_team = params.get('away_team')
    home_goals = params.get('home_goals')
    away_goals = params.get('away_goals')
    if not all([home_team, away_team, home_goals is not None, away_goals is not None]):
        return "Формат: резултат [домакин]-[гост] [домакин_голове]:[гост_голове] запиши"
    return matches.save_result(home_team, away_team, home_goals, away_goals)


# ---------------------------------------------------------------------------
# Handler C: Гол <Играч> <Отбор> <минута> минута
# ---------------------------------------------------------------------------
def handle_add_goal(params):
    player_name = params.get('player_name') or params.get('player_identifier')
    team_name = params.get('team_name') or params.get('club_identifier')
    minute = params.get('minute')
    if not player_name or not team_name or minute is None:
        return "Формат: гол [играч] [отбор] [минута] минута"
    return matches.add_goal_event(player_name, team_name, minute)


# ---------------------------------------------------------------------------
# Handler D: Избери мач <match_id>
# ---------------------------------------------------------------------------
def handle_select_match(params):
    match_id = params.get('match_id')
    if not match_id:
        return "Формат: избери мач [ID]"
    try:
        match_id = int(match_id)
    except (ValueError, TypeError):
        return "ID на мача трябва да бъде цяло число."
    return matches.select_match(match_id)


# ---------------------------------------------------------------------------
# Handler E: Картон <Играч> <Отбор> <Y/R> <минута>
# ---------------------------------------------------------------------------
def handle_add_card(params):
    player_name = params.get('player_name') or params.get('player_identifier')
    team_name = params.get('team_name') or params.get('club_identifier')
    card_type = params.get('card_type')
    minute = params.get('minute')
    if not player_name or not team_name or not card_type or minute is None:
        return "Формат: картон [играч] [отбор] [Y/R] [минута]"
    return matches.add_card_event(player_name, team_name, card_type, minute)


# ---------------------------------------------------------------------------
# Handler F: Покажи събития or Покажи събития <match_id>
# ---------------------------------------------------------------------------
def handle_show_events(params):
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
