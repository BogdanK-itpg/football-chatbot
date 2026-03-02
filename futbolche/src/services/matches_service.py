from db import fetch_one, fetch_all, execute
import services.players_service as players
from typing import Optional


def _resolve_club_id(club_identifier):
    if not club_identifier:
        return None
    try:
        cid = int(club_identifier)
        row = fetch_one("SELECT id FROM clubs WHERE id = ?", (cid,))
        if row:
            return row['id']
    except Exception:
        pass

    row = fetch_one("SELECT id FROM clubs WHERE LOWER(name) = LOWER(?)", (str(club_identifier),))
    return row['id'] if row else None


def record_match(home_team_id, away_team_id, match_date, home_goals=None, away_goals=None, league_id=None):
    """Insert a match record. Goals may be None for unplayed fixtures."""
    hid = _resolve_club_id(home_team_id)
    aid = _resolve_club_id(away_team_id)
    if not hid or not aid:
        return "Един от клубовете не съществува."
    if hid == aid:
        return "Двата отбора не могат да бъдат едни и същи."

    try:
        res = execute(
            "INSERT INTO matches (home_team_id, away_team_id, match_date, home_goals, away_goals, league_id) VALUES (?, ?, ?, ?, ?, ?)",
            (hid, aid, match_date, home_goals, away_goals, league_id)
        )
        if res is None:
            return "Грешка при запис на мача."
        return f"Мачът беше записан с ID {res}."
    except Exception:
        return "Грешка при запис на мача."


def get_match(match_id):
    row = fetch_one(
        "SELECT m.*, hc.name as home_name, ac.name as away_name FROM matches m JOIN clubs hc ON m.home_team_id = hc.id JOIN clubs ac ON m.away_team_id = ac.id WHERE m.id = ?",
        (match_id,)
    )
    if not row:
        return None
    return row


def compute_club_stats(club_identifier):
    cid = _resolve_club_id(club_identifier)
    if not cid:
        return "Клубът не съществува."

    rows = fetch_all(
        "SELECT m.*, hc.name as home_name, ac.name as away_name FROM matches m JOIN clubs hc ON m.home_team_id = hc.id JOIN clubs ac ON m.away_team_id = ac.id WHERE m.home_team_id = ? OR m.away_team_id = ?",
        (cid, cid)
    )

    if not rows:
        return {
            'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
        }

    stats = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
    for r in rows:
        hg = r['home_goals'] if r['home_goals'] is not None else 0
        ag = r['away_goals'] if r['away_goals'] is not None else 0
        is_home = (r['home_team_id'] == cid)
        is_away = (r['away_team_id'] == cid)
        # Only count played matches (both goals not None)
        if r['home_goals'] is None or r['away_goals'] is None:
            continue
        stats['P'] += 1
        if is_home:
            stats['GF'] += hg
            stats['GA'] += ag
            if hg > ag:
                stats['W'] += 1
                stats['Pts'] += 3
            elif hg < ag:
                stats['L'] += 1
            else:
                stats['D'] += 1
                stats['Pts'] += 1
        elif is_away:
            stats['GF'] += ag
            stats['GA'] += hg
            if ag > hg:
                stats['W'] += 1
                stats['Pts'] += 3
            elif ag < hg:
                stats['L'] += 1
            else:
                stats['D'] += 1
                stats['Pts'] += 1

    stats['GD'] = stats['GF'] - stats['GA']
    return stats


def get_league_fixtures(league_identifier):
    # resolve league id
    lid = None
    try:
        lid = int(league_identifier)
    except Exception:
        row = fetch_one("SELECT id FROM leagues WHERE LOWER(name)=LOWER(?)", (league_identifier,))
        if row:
            lid = row['id']

    if not lid:
        return "Лигата не съществува."

    rows = fetch_all("SELECT m.*, hc.name as home_name, ac.name as away_name FROM matches m JOIN clubs hc ON m.home_team_id = hc.id JOIN clubs ac ON m.away_team_id = ac.id WHERE m.league_id = ? ORDER BY m.match_date", (lid,))
    if not rows:
        return "Няма мачове за тази лига."

    out = []
    for r in rows:
        date = r['match_date']
        hg = r['home_goals'] if r['home_goals'] is not None else '-'
        ag = r['away_goals'] if r['away_goals'] is not None else '-'
        out.append(f"{date}: {r['home_name']} {hg}-{ag} {r['away_name']}")
    return "\n".join(out)


def _resolve_match_id(match_identifier) -> Optional[int]:
    if not match_identifier:
        return None
    try:
        mid = int(match_identifier)
        row = fetch_one("SELECT id FROM matches WHERE id = ?", (mid,))
        if row:
            return row['id']
    except Exception:
        pass
    return None


def record_event(match_identifier, player_identifier, event_type, minute=None):
    """Record a match event (goal, assist, yellow, red, appearance).

    If event_type is 'goal' the match goals are incremented for the player's team.
    """
    allowed = ('goal', 'assist', 'yellow', 'red', 'appearance')
    if event_type not in allowed:
        return "Невалиден тип събитие. Допустими: goal, assist, yellow, red, appearance."

    mid = _resolve_match_id(match_identifier)
    if not mid:
        return "Мачът не е намерен. Моля укажете валиден ID на мача."

    pid = None
    if player_identifier:
        pid = players.get_player_id(player_identifier)
        if not pid:
            return f"Играч '{player_identifier}' не съществува."

    try:
        res = execute(
            "INSERT INTO events (match_id, player_id, event_type, minute) VALUES (?, ?, ?, ?)",
            (mid, pid, event_type, minute)
        )
        if res is None:
            return "Грешка при запис на събитието."

        # If goal, update match goals depending on player's club
        if event_type == 'goal' and pid is not None:
            p = fetch_one("SELECT club_id FROM players WHERE id = ?", (pid,))
            m = fetch_one("SELECT home_team_id, away_team_id, home_goals, away_goals FROM matches WHERE id = ?", (mid,))
            if p and m:
                try:
                    if p['club_id'] == m['home_team_id']:
                        execute("UPDATE matches SET home_goals = ? WHERE id = ?", ( (m['home_goals'] or 0) + 1, mid))
                    elif p['club_id'] == m['away_team_id']:
                        execute("UPDATE matches SET away_goals = ? WHERE id = ?", ( (m['away_goals'] or 0) + 1, mid))
                except Exception:
                    pass

        return "Събитието беше записано успешно."
    except Exception:
        return "Грешка при запис на събитието."


def get_match_events(match_identifier):
    mid = _resolve_match_id(match_identifier)
    if not mid:
        return "Мачът не е намерен."
    rows = fetch_all(
        "SELECT e.*, p.full_name as player_name FROM events e LEFT JOIN players p ON e.player_id = p.id WHERE e.match_id = ? ORDER BY COALESCE(e.minute, 0)",
        (mid,)
    )
    if not rows:
        return "Няма записани събития за този мач."
    out = []
    for r in rows:
        minute = r['minute'] if r['minute'] is not None else '-'
        player = r['player_name'] or 'Unknown'
        out.append(f"{minute}' - {r['event_type']} - {player}")
    return "\n".join(out)


def get_league_standings(league_identifier):
    # resolve league id
    lid = None
    try:
        lid = int(league_identifier)
    except Exception:
        row = fetch_one("SELECT id FROM leagues WHERE LOWER(name)=LOWER(?)", (league_identifier,))
        if row:
            lid = row['id']

    if not lid:
        return "Лигата не съществува."

    teams = fetch_all("SELECT lt.club_id, c.name FROM league_teams lt JOIN clubs c ON lt.club_id = c.id WHERE lt.league_id = ?", (lid,))
    if not teams:
        return "Няма отбори в тази лига."

    table = []
    for t in teams:
        cid = t['club_id']
        rows = fetch_all("SELECT * FROM matches WHERE league_id = ? AND (home_team_id = ? OR away_team_id = ?)", (lid, cid, cid))
        stats = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0}
        for r in rows:
            # skip matches without recorded goals (consider played if home_goals or away_goals is not null)
            if r['home_goals'] is None or r['away_goals'] is None:
                continue
            hg = r['home_goals']
            ag = r['away_goals']
            is_home = (r['home_team_id'] == cid)
            is_away = (r['away_team_id'] == cid)
            stats['P'] += 1
            if is_home:
                stats['GF'] += hg
                stats['GA'] += ag
                if hg > ag:
                    stats['W'] += 1
                    stats['Pts'] += 3
                elif hg < ag:
                    stats['L'] += 1
                else:
                    stats['D'] += 1
                    stats['Pts'] += 1
            elif is_away:
                stats['GF'] += ag
                stats['GA'] += hg
                if ag > hg:
                    stats['W'] += 1
                    stats['Pts'] += 3
                elif ag < hg:
                    stats['L'] += 1
                else:
                    stats['D'] += 1
                    stats['Pts'] += 1

        stats['GD'] = stats['GF'] - stats['GA']
        table.append({
            'club_id': cid,
            'club_name': t['name'],
            'played': stats['P'],
            'wins': stats['W'],
            'draws': stats['D'],
            'losses': stats['L'],
            'goals_for': stats['GF'],
            'goals_against': stats['GA'],
            'goal_difference': stats['GD'],
            'points': stats['Pts']
        })

    # sort by points, GD, GF, name
    table.sort(key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for'], x['club_name']))

    out = []
    pos = 1
    for row in table:
        out.append(f"{pos}. {row['club_name']} — P:{row['played']} W:{row['wins']} D:{row['draws']} L:{row['losses']} GF:{row['goals_for']} GA:{row['goals_against']} GD:{row['goal_difference']} Pts:{row['points']}")
        pos += 1

    return "\n".join(out)
