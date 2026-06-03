from repositories import clubs_repo, players_repo, matches_repo, events_repo


def get_club_statistics(identifier):
    cid = _resolve_club_id(identifier)
    if not cid:
        return None
    all_matches = matches_repo.get_by_league(None) or []
    all_matches += [m for m in (matches_repo.get_all() or []) if m not in all_matches]

    # Filter matches involving this club
    club_matches = [
        m for m in (matches_repo.get_all() or [])
        if (m['home_team_id'] == cid or m['away_team_id'] == cid)
        and m['home_goals'] is not None and m['away_goals'] is not None
    ]

    played = len(club_matches)
    wins = 0
    draws = 0
    goals_for = 0
    goals_against = 0

    for m in club_matches:
        if m['home_team_id'] == cid:
            gf = m['home_goals']
            ga = m['away_goals']
        else:
            gf = m['away_goals']
            ga = m['home_goals']
        goals_for += gf
        goals_against += ga
        if gf > ga:
            wins += 1
        elif gf == ga:
            draws += 1

    losses = played - wins - draws
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


def get_player_statistics(identifier):
    pid = _resolve_player_id(identifier)
    if not pid:
        return None

    goals = events_repo.count_by_player(pid, 'goal')
    assists = events_repo.count_by_player(pid, 'assist')
    yellows = events_repo.count_by_player(pid, 'yellow')
    reds = events_repo.count_by_player(pid, 'red')
    appearances = events_repo.count_by_player(pid, 'appearance')

    return {
        'player_id': pid,
        'goals': goals,
        'assists': assists,
        'appearances': appearances,
        'yellow_cards': yellows,
        'red_cards': reds
    }


def get_player_advanced_metrics(identifier):
    stats = get_player_statistics(identifier)
    if not stats:
        return None
    appearances = stats.get('appearances', 0) or 0
    minutes_played = appearances * 90
    goals = stats.get('goals', 0) or 0
    assists = stats.get('assists', 0) or 0
    if minutes_played > 0:
        goals_per_90 = round((goals * 90) / minutes_played, 2)
        assists_per_90 = round((assists * 90) / minutes_played, 2)
    else:
        goals_per_90 = 0.0
        assists_per_90 = 0.0
    return {
        'player_id': stats['player_id'],
        'minutes_played': minutes_played,
        'goals_per_90': goals_per_90,
        'assists_per_90': assists_per_90
    }


def _resolve_club_id(identifier):
    if not identifier:
        return None
    if str(identifier).isdigit():
        club = clubs_repo.get_by_id(int(identifier))
        if club:
            return club['id']
    club = clubs_repo.get_by_name(identifier)
    return club['id'] if club else None


def _resolve_player_id(identifier):
    if not identifier:
        return None
    if str(identifier).isdigit():
        p = players_repo.get_by_id(int(identifier))
        if p:
            return p['id']
    p = players_repo.get_by_name(identifier)
    return p['id'] if p else None
