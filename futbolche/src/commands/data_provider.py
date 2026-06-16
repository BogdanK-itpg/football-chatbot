from typing import List, Tuple


def get_options_for_param(param_name: str, intent_tag: str = "") -> List[Tuple[str, str]]:
    if not param_name:
        return []
    name_lower = param_name.lower()

    if name_lower in ("from_club",):
        return _get_from_club_options()
    if name_lower in ("to_club_identifier", "team_name", "team1", "team2", "home_team", "away_team"):
        return _get_club_options()
    if "club" in name_lower and name_lower not in ("to_club_identifier", "from_club"):
        return _get_club_options()
    if "player" in name_lower:
        return _get_player_options()
    if "league" in name_lower:
        return _get_league_options()
    if name_lower == "match_id":
        only_unplayed = intent_tag in ("record_event", "end_match")
        return _get_match_options(only_unplayed=only_unplayed)
    if "season" in name_lower or name_lower == "season":
        return _get_season_options()
    return []


def _get_from_club_options() -> List[Tuple[str, str]]:
    options = _get_club_options()
    options.insert(0, ("--- Свободен агент ---", "няма"))
    return options


def _get_club_options() -> List[Tuple[str, str]]:
    try:
        from repositories import clubs_repo
        rows = clubs_repo.get_all()
        if not rows:
            return []
        return [(r["name"], r["name"]) for r in rows]
    except Exception:
        return []


def _get_player_options() -> List[Tuple[str, str]]:
    try:
        from repositories import players_repo
        rows = players_repo.get_all()
        if not rows:
            return []
        result = []
        for r in rows:
            club = r["club_name"] if r["club_name"] else "без клуб"
            number = r["number"] if r["number"] is not None else "-"
            display = f"{r['full_name']} ({club} #{number})"
            result.append((display, r["full_name"]))
        return result
    except Exception:
        return []


def _get_league_options() -> List[Tuple[str, str]]:
    try:
        from repositories import leagues_repo
        rows = leagues_repo.get_all()
        if not rows:
            return []
        return [(f"{r['name']} ({r['season']})", str(r["id"])) for r in rows]
    except Exception:
        return []


def _get_match_options(only_unplayed: bool = False) -> List[Tuple[str, str]]:
    try:
        from repositories import matches_repo
        rows = matches_repo.get_all()
        if not rows:
            return []
        result = []
        for r in rows:
            if only_unplayed and r["is_played"]:
                continue
            is_played = r["is_played"]
            hg = r["home_goals"] if is_played else "?"
            ag = r["away_goals"] if is_played else "?"
            display = f"#{r['id']} {r['home_name']} {hg}:{ag} {r['away_name']} ({r['match_date']})"
            result.append((display, str(r["id"])))
        return result
    except Exception:
        return []


def _get_season_options() -> List[Tuple[str, str]]:
    try:
        from repositories import leagues_repo
        rows = leagues_repo.get_all()
        if not rows:
            return [("2025", "2025")]
        seen = set()
        result = []
        for r in rows:
            s = r["season"]
            if s not in seen:
                seen.add(s)
                result.append((s, s))
        return result if result else [("2025", "2025")]
    except Exception:
        return [("2025", "2025")]
