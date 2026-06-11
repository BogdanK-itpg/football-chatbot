from typing import Optional
from repositories import clubs_repo, players_repo, matches_repo, events_repo, leagues_repo
import state
from validators import validate_minute, validate_score, validate_no_duplicate_result, \
    validate_player_in_match, validate_no_goal_after_red, \
    validate_card_allowed, validate_player_belongs_to_club


def _resolve_club_id(club_identifier):
    if not club_identifier:
        return None
    cid = club_identifier.strip()
    if cid.isdigit():
        club = clubs_repo.get_by_id(int(cid))
        if club:
            return club['id']
    club = clubs_repo.get_by_name(cid)
    return club['id'] if club else None


def record_match(home_team_id, away_team_id, match_date, home_goals=None, away_goals=None, league_id=None, round_no=None):
    hid = _resolve_club_id(home_team_id)
    aid = _resolve_club_id(away_team_id)
    if not hid or not aid:
        return "Един от клубовете не съществува."
    if hid == aid:
        return "Двата отбора не могат да бъдат едни и същи."
    if league_id:
        resolved_league = leagues_repo.resolve_id(league_id)
        if not resolved_league:
            return f"Лига '{league_id}' не съществува."
        league_id = resolved_league
    if round_no:
        try:
            round_no = int(round_no)
        except (ValueError, TypeError):
            return "Номерът на кръга трябва да бъде цяло число."
    try:
        res = matches_repo.create(hid, aid, match_date, home_goals, away_goals, league_id, round_no)
        if res is None:
            return "Грешка при запис на мача."
        if home_goals is not None and away_goals is not None:
            matches_repo.set_played(res)
        return f"Мачът беше записан с ID {res}."
    except Exception:
        return "Грешка при запис на мача."


def save_result(home_team, away_team, home_goals, away_goals):
    valid, err = validate_score(home_goals, away_goals)
    if not valid:
        return err
    home_club = clubs_repo.get_by_name(home_team) if not home_team.isdigit() else clubs_repo.get_by_id(int(home_team))
    away_club = clubs_repo.get_by_name(away_team) if not away_team.isdigit() else clubs_repo.get_by_id(int(away_team))
    if not home_club:
        return f"Клуб '{home_team}' не съществува."
    if not away_club:
        return f"Клуб '{away_team}' не съществува."
    match_id = state.get_current_match()
    if match_id:
        match = matches_repo.get_by_id(match_id)
        if not match:
            return "Избраният мач не е намерен."
        if match['home_team_id'] != home_club['id'] or match['away_team_id'] != away_club['id']:
            return "Избраният мач не съответства на посочените отбори."
    else:
        all_m = matches_repo.get_all()
        match = None
        for m in all_m:
            if (m['home_team_id'] == home_club['id'] and m['away_team_id'] == away_club['id']) \
               and not m['is_played']:
                match = m
                break
        if not match:
            return "Няма намерен неплаиран мач между тези отбори. Използвайте 'избери мач [ID]' първо."
    valid, err = validate_no_duplicate_result(match['id'])
    if not valid:
        return err
    res = matches_repo.set_score(match['id'], int(home_goals), int(away_goals))
    if res is None:
        return "Грешка при запис на резултата."
    return (f"Резултатът {int(home_goals)}:{int(away_goals)} за мач "
            f"{match['id']} ({match['home_name']} vs {match['away_name']}) беше записан успешно.")


def add_goal_event(player_name, team_name, minute):
    valid, err = validate_minute(minute)
    if not valid:
        return err
    player = players_repo.get_by_name(player_name)
    if not player:
        return f"Играч '{player_name}' не съществува."
    pid = player['id']
    valid, err = validate_player_belongs_to_club(pid, team_name)
    if not valid:
        return err
    club = clubs_repo.get_by_name(team_name)
    if not club:
        return f"Клуб '{team_name}' не съществува."
    match_id = state.get_current_match()
    if not match_id:
        return "Няма избран мач. Използвайте 'избери мач [ID]' първо."
    valid, err = validate_player_in_match(pid, match_id)
    if not valid:
        return err
    if matches_repo.is_played(match_id):
        return "Мачът вече е приключил. Не можете да добавяте голове след като резултатът е записан."
    valid, err = validate_no_goal_after_red(pid, match_id)
    if not valid:
        return err
    result = record_event(match_id, pid, club['id'], 'goal', minute=int(minute))
    if "успешно" not in result.lower():
        return result
    match = matches_repo.get_by_id(match_id)
    if match:
        is_home = (club['id'] == match['home_team_id'])
        matches_repo.increment_score(match_id, is_home)
    return f"Гол за {player_name} в {minute}' минута — записан успешно."


def add_card_event(player_name, team_name, card_type, minute):
    card_type = card_type.upper()
    if card_type not in ('Y', 'R'):
        return "Типът картон трябва да бъде Y (жълт) или R (червен)."
    valid, err = validate_minute(minute)
    if not valid:
        return err
    player = players_repo.get_by_name(player_name)
    if not player:
        return f"Играч '{player_name}' не съществува."
    pid = player['id']
    valid, err = validate_player_belongs_to_club(pid, team_name)
    if not valid:
        return err
    club = clubs_repo.get_by_name(team_name)
    if not club:
        return f"Клуб '{team_name}' не съществува."
    match_id = state.get_current_match()
    if not match_id:
        return "Няма избран мач. Използвайте 'избери мач [ID]' първо."
    valid, err = validate_player_in_match(pid, match_id)
    if not valid:
        return err
    valid, err = validate_card_allowed(pid, match_id, card_type)
    if not valid:
        return err
    event_type = 'red' if card_type == 'R' else 'yellow'
    actual_card_type = card_type
    if card_type == 'Y':
        existing = events_repo.count_cards_in_match(match_id, pid)
        if existing['yellow'] >= 1:
            event_type = 'red'
            actual_card_type = 'R'
    return record_event(match_id, pid, club['id'], event_type,
                        minute=int(minute), card_type=actual_card_type)


def select_match(match_id):
    if not matches_repo.exists(match_id):
        return f"Мач с ID {match_id} не съществува."
    state.set_current_match(match_id)
    match = matches_repo.get_by_id(match_id)
    return (f"Избран мач ID {match_id}: {match['home_name']} vs {match['away_name']} "
            f"({match['match_date']}).")


def show_round(round_no, league_name):
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


def get_match(match_id):
    return matches_repo.get_by_id(match_id)


def get_match_events(match_identifier):
    mid = _resolve_match_id(match_identifier)
    if not mid:
        return "Мачът не е намерен."
    rows = events_repo.get_by_match(mid)
    if not rows:
        return "Няма записани събития за този мач."
    out = []
    for r in rows:
        minute = r['minute'] if r['minute'] is not None else '-'
        player = r['player_name'] or 'Unknown'
        ev_type = r['event_type']
        if ev_type == 'goal':
            suffix = ' (автогол)' if r['is_own_goal'] else ''
            out.append(f"{minute}' - ГОЛ - {player}{suffix}")
        elif ev_type in ('yellow', 'red'):
            card = 'ЧВ' if ev_type == 'red' else 'ЖК'
            out.append(f"{minute}' - {card} - {player}")
        elif ev_type == 'assist':
            out.append(f"{minute}' - АСИСТЕНЦИЯ - {player}")
        elif ev_type == 'appearance':
            out.append(f"{minute}' - ПОЯВА - {player}")
        else:
            out.append(f"{minute}' - {ev_type} - {player}")
    return "\n".join(out)


def get_league_fixtures(league_identifier):
    lid = _resolve_league_id(league_identifier)
    if not lid:
        return "Лигата не съществува."
    rows = matches_repo.get_by_league(lid)
    if not rows:
        return "Няма мачове за тази лига."
    out = []
    for r in rows:
        date = r['match_date']
        hg = r['home_goals'] if r['home_goals'] is not None else '-'
        ag = r['away_goals'] if r['away_goals'] is not None else '-'
        out.append(f"{date}: {r['home_name']} {hg}-{ag} {r['away_name']}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Event recording (used by handlers AFTER validation)
# ---------------------------------------------------------------------------

def record_event(match_id, player_id, club_id, event_type, minute=None, card_type=None, is_own_goal=0):
    """Record a match event. Validation must happen BEFORE calling this."""
    res = events_repo.create(match_id, player_id, club_id, event_type, minute, card_type, is_own_goal)
    if res is None:
        return "Грешка при запис на събитието."
    return "Събитието беше записано успешно."


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_match_id(match_identifier) -> Optional[int]:
    if not match_identifier:
        return None
    try:
        mid = int(match_identifier)
        if matches_repo.exists(mid):
            return mid
    except Exception:
        pass
    return None


def _resolve_league_id(league_identifier):
    if not league_identifier:
        return None
    return leagues_repo.resolve_id(league_identifier)



