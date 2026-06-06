from typing import Optional
from db import fetch_one, fetch_all, execute


def get_by_id(match_id: int):
    return fetch_one(
        """SELECT m.*, hc.name as home_name, ac.name as away_name
           FROM matches m
           JOIN clubs hc ON m.home_team_id = hc.id
           JOIN clubs ac ON m.away_team_id = ac.id
           WHERE m.id = ?""",
        (match_id,)
    )


def get_by_league(league_id: int, round_no: Optional[int] = None):
    if round_no is not None:
        return fetch_all(
            """SELECT m.*, hc.name as home_name, ac.name as away_name
               FROM matches m
               JOIN clubs hc ON m.home_team_id = hc.id
               JOIN clubs ac ON m.away_team_id = ac.id
               WHERE m.league_id = ? AND m.round_no = ?
               ORDER BY m.match_date""",
            (league_id, round_no)
        )
    return fetch_all(
        """SELECT m.*, hc.name as home_name, ac.name as away_name
           FROM matches m
           JOIN clubs hc ON m.home_team_id = hc.id
           JOIN clubs ac ON m.away_team_id = ac.id
           WHERE m.league_id = ?
           ORDER BY m.match_date""",
        (league_id,)
    )


def get_by_date(match_date: str):
    return fetch_all(
        """SELECT m.*, hc.name as home_name, ac.name as away_name
           FROM matches m
           JOIN clubs hc ON m.home_team_id = hc.id
           JOIN clubs ac ON m.away_team_id = ac.id
           WHERE m.match_date = ?
           ORDER BY m.id""",
        (match_date,)
    )


def get_all():
    return fetch_all(
        """SELECT m.*, hc.name as home_name, ac.name as away_name
           FROM matches m
           JOIN clubs hc ON m.home_team_id = hc.id
           JOIN clubs ac ON m.away_team_id = ac.id
           ORDER BY m.match_date"""
    )


def create(home_team_id: int, away_team_id: int, match_date: str,
           home_goals=None, away_goals=None, league_id=None, round_no=None):
    if home_team_id == away_team_id:
        return None
    return execute(
        "INSERT INTO matches (home_team_id, away_team_id, match_date, home_goals, away_goals, league_id, round_no) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (home_team_id, away_team_id, match_date, home_goals, away_goals, league_id, round_no)
    )


def set_score(match_id: int, home_goals: int, away_goals: int):
    return execute(
        "UPDATE matches SET home_goals = ?, away_goals = ?, is_played = 1 WHERE id = ?",
        (home_goals, away_goals, match_id)
    )


def set_played(match_id: int):
    return execute("UPDATE matches SET is_played = 1 WHERE id = ?", (match_id,))


def increment_score(match_id: int, is_home: bool):
    if is_home:
        return execute(
            "UPDATE matches SET home_goals = COALESCE(home_goals, 0) + 1 WHERE id = ?",
            (match_id,)
        )
    return execute(
        "UPDATE matches SET away_goals = COALESCE(away_goals, 0) + 1 WHERE id = ?",
        (match_id,)
    )


def exists(match_id: int) -> bool:
    row = fetch_one("SELECT 1 FROM matches WHERE id = ?", (match_id,))
    return row is not None


def is_played(match_id: int) -> bool:
    row = fetch_one("SELECT is_played FROM matches WHERE id = ?", (match_id,))
    return row is not None and row['is_played'] == 1
