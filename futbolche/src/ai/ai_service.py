from repositories import clubs_repo, leagues_repo
from ai import features
from ai import probability


def _get_team_id(team_name):
    club = clubs_repo.get_by_name(team_name)
    return club['id'] if club else None


def _find_common_league(home_team_id, away_team_id):
    all_leagues = leagues_repo.get_all() or []
    for league in all_leagues:
        teams = leagues_repo.get_teams(league['id']) or []
        team_ids = {t['id'] for t in teams}
        if home_team_id in team_ids and away_team_id in team_ids:
            return league['id']
    return None


def predict_match(home_team_name, away_team_name):
    home_team_id = _get_team_id(home_team_name)
    away_team_id = _get_team_id(away_team_name)

    if not home_team_id or not away_team_id:
        raise ValueError("Team does not exist")

    league_id = _find_common_league(home_team_id, away_team_id)
    if league_id is None:
        raise ValueError("Teams are from different leagues")

    home_matches = features.get_last_matches(home_team_id, 5)
    away_matches = features.get_last_matches(away_team_id, 5)

    if len(home_matches) < 5 or len(away_matches) < 5:
        raise ValueError("Not enough matches played")

    home_features = features.build_team_features(home_team_id, league_id)
    away_features = features.build_team_features(away_team_id, league_id)

    return probability.calculate_probabilities(home_features, away_features)
