"""Handlers for match commands — thin wrappers over matches_service."""

import services.matches_service as matches


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
# Handler B: Покажи събития <match_id>
# ---------------------------------------------------------------------------
def handle_show_events(params):
    match_id = params.get('match_id')
    if not match_id:
        return "Формат: покажи събития [match_id]"
    return matches.get_match_events(match_id)
