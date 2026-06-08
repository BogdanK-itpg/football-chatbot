from repositories import matches_repo, leagues_repo
from services.standings_service import calculate_standings


def get_last_matches(team_id, limit=5):
    all_matches = matches_repo.get_all() or []
    team_matches = []
    for m in all_matches:
        if m['is_played'] and m['home_goals'] is not None and m['away_goals'] is not None:
            if m['home_team_id'] == team_id or m['away_team_id'] == team_id:
                team_matches.append(m)
    team_matches.sort(key=lambda x: x['match_date'], reverse=True)
    return team_matches[:limit]


def calculate_form(team_id):
    matches = get_last_matches(team_id, 5)
    if not matches:
        return 0.0
    points = 0
    for m in matches:
        if m['home_team_id'] == team_id:
            gf, ga = m['home_goals'], m['away_goals']
        else:
            gf, ga = m['away_goals'], m['home_goals']
        if gf > ga:
            points += 3
        elif gf == ga:
            points += 1
    return points / 15.0


def calculate_attack_strength(team_id):
    matches = get_last_matches(team_id, 5)
    if not matches:
        return 0.0
    total_goals = 0
    for m in matches:
        if m['home_team_id'] == team_id:
            total_goals += m['home_goals']
        else:
            total_goals += m['away_goals']
    return total_goals / len(matches)


def calculate_defense_strength(team_id):
    matches = get_last_matches(team_id, 5)
    if not matches:
        return 0.0
    total_conceded = 0
    for m in matches:
        if m['home_team_id'] == team_id:
            total_conceded += m['away_goals']
        else:
            total_conceded += m['home_goals']
    avg_conceded = total_conceded / len(matches)
    return 1 / (1 + avg_conceded)


def calculate_ranking_score(team_id, league_id):
    league = leagues_repo.get_by_id(league_id)
    if not league:
        return 0.0
    table = calculate_standings(league['name'], league['season'])
    if not table:
        return 0.0
    total_teams = len(table)
    for row in table:
        if row['team_id'] == team_id:
            return (total_teams - row['position'] + 1) / total_teams
    return 0.0


def build_team_features(team_id, league_id=None):
    return {
        'form': calculate_form(team_id),
        'attack': calculate_attack_strength(team_id),
        'defense': calculate_defense_strength(team_id),
        'ranking': calculate_ranking_score(team_id, league_id) if league_id else 0.0
    }
