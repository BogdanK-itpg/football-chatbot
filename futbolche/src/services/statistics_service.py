from db import fetch_one, fetch_all, fetch_all as fetchAll, fetch_one as fetchOne


def _resolve_club_id(identifier):
    # identifier may be int or name
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        return int(identifier)
    row = fetch_one("SELECT id FROM clubs WHERE LOWER(name) = LOWER(?)", (str(identifier),))
    if row:
        return row['id']
    # try contains
    rows = fetch_all("SELECT id, name FROM clubs")
    for r in rows:
        if str(identifier).casefold() in r['name'].casefold():
            return r['id']
    return None


def get_club_statistics(identifier):
    """Return aggregated statistics for a club: matches, wins, draws, losses, goals for/against, points."""
    cid = _resolve_club_id(identifier)
    if not cid:
        return None

    played_q = "SELECT COUNT(*) as cnt FROM matches WHERE home_team_id = ? OR away_team_id = ?"
    played = fetch_one(played_q, (cid, cid))['cnt'] or 0

    wins_home = fetch_one("SELECT COUNT(*) as cnt FROM matches WHERE home_team_id = ? AND home_goals > away_goals", (cid,))['cnt'] or 0
    wins_away = fetch_one("SELECT COUNT(*) as cnt FROM matches WHERE away_team_id = ? AND away_goals > home_goals", (cid,))['cnt'] or 0
    wins = wins_home + wins_away

    draws = fetch_one("SELECT COUNT(*) as cnt FROM matches WHERE (home_team_id = ? OR away_team_id = ?) AND home_goals = away_goals", (cid, cid))['cnt'] or 0
    losses = (played - wins - draws) if played is not None else 0

    gf_home = fetch_one("SELECT COALESCE(SUM(home_goals),0) as s FROM matches WHERE home_team_id = ?", (cid,))['s'] or 0
    gf_away = fetch_one("SELECT COALESCE(SUM(away_goals),0) as s FROM matches WHERE away_team_id = ?", (cid,))['s'] or 0
    goals_for = gf_home + gf_away

    ga_home = fetch_one("SELECT COALESCE(SUM(away_goals),0) as s FROM matches WHERE home_team_id = ?", (cid,))['s'] or 0
    ga_away = fetch_one("SELECT COALESCE(SUM(home_goals),0) as s FROM matches WHERE away_team_id = ?", (cid,))['s'] or 0
    goals_against = ga_home + ga_away

    goal_diff = goals_for - goals_against
    points = wins * 3 + draws

    return {
        'club_id': cid,
        'played': played,
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'goals_for': goals_for,
        'goals_against': goals_against,
        'goal_difference': goal_diff,
        'points': points
    }


def _resolve_player_id(identifier):
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        return int(identifier)
    row = fetch_one("SELECT id FROM players WHERE LOWER(full_name) = LOWER(?)", (str(identifier),))
    if row:
        return row['id']
    rows = fetch_all("SELECT id, full_name FROM players")
    for r in rows:
        if str(identifier).casefold() in r['full_name'].casefold():
            return r['id']
    return None


def get_player_statistics(identifier):
    pid = _resolve_player_id(identifier)
    if not pid:
        return None

    goals = fetch_one("SELECT COUNT(*) as cnt FROM events WHERE player_id = ? AND event_type = 'goal'", (pid,))['cnt'] or 0
    assists = fetch_one("SELECT COUNT(*) as cnt FROM events WHERE player_id = ? AND event_type = 'assist'", (pid,))['cnt'] or 0
    yellows = fetch_one("SELECT COUNT(*) as cnt FROM events WHERE player_id = ? AND event_type = 'yellow'", (pid,))['cnt'] or 0
    reds = fetch_one("SELECT COUNT(*) as cnt FROM events WHERE player_id = ? AND event_type = 'red'", (pid,))['cnt'] or 0
    appearances = fetch_one("SELECT COUNT(*) as cnt FROM events WHERE player_id = ? AND event_type = 'appearance'", (pid,))['cnt'] or 0

    return {
        'player_id': pid,
        'goals': goals,
        'assists': assists,
        'appearances': appearances,
        'yellow_cards': yellows,
        'red_cards': reds
    }
