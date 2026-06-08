from typing import Optional
from db import fetch_one, fetch_all


def get_league_by_name_and_season(name: str, season: str):
    return fetch_one(
        "SELECT * FROM leagues WHERE LOWER(name) = LOWER(?) AND LOWER(season) = LOWER(?)",
        (name.strip(), season.strip())
    )


def get_league_by_name(name: str):
    return fetch_one("SELECT * FROM leagues WHERE LOWER(name) = LOWER(?)", (name.strip(),))


def get_league_by_id(league_id: int):
    return fetch_one("SELECT * FROM leagues WHERE id = ?", (league_id,))


def get_league_teams(league_id: int):
    return fetch_all(
        """SELECT c.id, c.name, c.city, c.founded_year
           FROM clubs c
           JOIN league_teams lt ON c.id = lt.club_id
           WHERE lt.league_id = ?
           ORDER BY c.name""",
        (league_id,)
    )


def get_played_matches(league_id: int):
    return fetch_all(
        """SELECT m.*, hc.name as home_name, ac.name as away_name
           FROM matches m
           JOIN clubs hc ON m.home_team_id = hc.id
           JOIN clubs ac ON m.away_team_id = ac.id
           WHERE m.league_id = ?
             AND m.is_played = 1
             AND m.home_goals IS NOT NULL
             AND m.away_goals IS NOT NULL
           ORDER BY m.id""",
        (league_id,)
    )


def validate_match_consistency(league_id: int):
    results = fetch_all(
        """SELECT m.id, m.home_team_id, m.away_team_id, m.home_goals, m.away_goals
           FROM matches m
           LEFT JOIN league_teams lt_home ON lt_home.league_id = ? AND lt_home.club_id = m.home_team_id
           LEFT JOIN league_teams lt_away ON lt_away.league_id = ? AND lt_away.club_id = m.away_team_id
           WHERE m.league_id = ?
             AND (lt_home.id IS NULL OR lt_away.id IS NULL)""",
        (league_id, league_id, league_id)
    )
    return results or []


def get_matches_with_scores_not_played(league_id: int):
    return fetch_all(
        """SELECT m.*, hc.name as home_name, ac.name as away_name
           FROM matches m
           JOIN clubs hc ON m.home_team_id = hc.id
           JOIN clubs ac ON m.away_team_id = ac.id
           WHERE m.league_id = ?
             AND m.is_played = 0
             AND m.home_goals IS NOT NULL
             AND m.away_goals IS NOT NULL""",
        (league_id,)
    )
