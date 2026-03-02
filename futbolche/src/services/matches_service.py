from db import fetch_one, fetch_all, execute


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
