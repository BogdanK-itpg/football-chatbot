from typing import Optional
from repositories import clubs_repo, players_repo, matches_repo, events_repo, leagues_repo


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



