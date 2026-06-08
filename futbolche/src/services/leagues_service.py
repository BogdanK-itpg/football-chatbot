from datetime import date, timedelta, datetime
import re
from typing import Optional
from repositories import leagues_repo, clubs_repo, matches_repo


def create_league(name: str, season: str):
    if not name or not name.strip():
        return "Името на лигата не може да бъде празно."
    if not season or not season.strip():
        return "Сезонът не може да бъде празен."
    season = season.strip()
    if not re.match(r'^\d{4}([\/-]\d{2,4})?$', season):
        return "Невалиден формат на сезон. Използвайте формат: 2025, 2025/26, 2025/2026 или 2025-2026."
    name_clean = name.strip()
    existing = leagues_repo.get_by_name_season(name_clean, season)
    if existing:
        return f"Лига с име '{name_clean}' и сезон '{season}' вече съществува."
    res = leagues_repo.create(name_clean, season)
    if res is None:
        return "Грешка при създаване на лига."
    return f"Лига '{name_clean}' ({season}) беше създадена успешно."


def add_club_to_league(league_identifier, club_identifier):
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return f"Няма лига с име/ID '{league_identifier}'."
    cid = None
    if str(club_identifier).isdigit():
        club = clubs_repo.get_by_id(int(club_identifier))
        if club:
            cid = club['id']
    else:
        club = clubs_repo.get_by_name(club_identifier)
        if club:
            cid = club['id']
    if not cid:
        return "Клубът не съществува."
    res = leagues_repo.add_team(lid, cid)
    if res is None:
        return "Грешка при добавяне на клуба в лигата (възможно дублиране)."
    return "Клубът беше добавен в лигата успешно."


def get_league_teams(league_identifier):
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return []
    rows = leagues_repo.get_teams(lid)
    return rows or []


def generate_round_robin(league_identifier, double_round: bool = False, start_date: Optional[str] = None, interval_days: int = 7):
    teams = get_league_teams(league_identifier)
    if not teams or len(teams) < 2:
        return "Недостатъчно отбори за създаване на кръгове."
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return f"Няма лига с име/ID '{league_identifier}'."

    existing = matches_repo.get_by_league(lid)
    if existing:
        return "Програмата за тази лига вече е генерирана."

    if start_date:
        try:
            current = datetime.strptime(start_date, "%Y-%m-%d").date()
        except Exception:
            current = date.today()
    else:
        current = date.today()

    club_ids = [t['id'] for t in teams]
    n = len(club_ids)

    # Circle Method for round-robin scheduling
    if n % 2 == 1:
        club_ids.append(None)  # BYE placeholder
        n += 1

    fixed = club_ids[0]
    rotating = club_ids[1:]
    total_rounds = n - 1
    created = 0

    def _schedule_round(round_no, home_first, away_first):
        nonlocal created, current
        fixtures = []
        for i in range(n // 2):
            if i == 0:
                home, away = fixed, rotating[n - 2]
            else:
                home, away = rotating[i - 1], rotating[n - 2 - i]
            if home is None or away is None:
                continue
            if (i == 0 and round_no % 2 == 1) or (i != 0 and round_no % 2 == 0):
                home, away = away, home
            fixtures.append((home, away))
        for home, away in fixtures:
            res = matches_repo.create(home, away, current.isoformat(), league_id=lid, round_no=round_no)
            if res:
                created += 1
        current += timedelta(days=interval_days)

    for round_no in range(1, total_rounds + 1):
        _schedule_round(round_no, True, True)
        rotating = [rotating[-1]] + rotating[:-1]

    if double_round:
        for round_no in range(total_rounds + 1, 2 * total_rounds + 1):
            _schedule_round(round_no, False, True)
            rotating = [rotating[-1]] + rotating[:-1]

    return f"Създадени {created} мача за лига {league_identifier}."


def get_standings(league_identifier):
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return f"Няма лига с име/ID '{league_identifier}'."
    from services.standings_service import calculate_standings
    league = leagues_repo.get_by_id(lid)
    if not league:
        return f"Няма лига с ID '{lid}'."
    table = calculate_standings(league['name'], league['season'])
    if not table:
        return "Няма отбори в тази лига."
    lines = []
    for row in table:
        lines.append(
            f"{row['position']}. {row['team']} | P:{row['mp']} W:{row['w']} D:{row['d']} L:{row['l']} "
            f"GF:{row['gf']} GA:{row['ga']} GD:{row['gd']} Pts:{row['pts']}"
        )
    return "\n".join(lines)


def remove_club_from_league(league_identifier, club_identifier):
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return "Лигата не съществува."
    cid = None
    if str(club_identifier).isdigit():
        club = clubs_repo.get_by_id(int(club_identifier))
        if club:
            cid = club['id']
    else:
        club = clubs_repo.get_by_name(club_identifier)
        if club:
            cid = club['id']
    if not cid:
        return "Клубът не съществува."
    existing = leagues_repo.get_teams(lid)
    if not any(t['id'] == cid for t in existing):
        return "Клубът не е в тази лига."
    schedule = matches_repo.get_by_league(lid)
    if schedule:
        return "Не можете да премахнете отбор, след като програмата е генерирана. Изтрийте програмата първо."
    res = leagues_repo.remove_team(lid, cid)
    if res is None:
        return "Грешка при премахване на клуба от лигата."
    return "Клубът беше премахнат от лигата успешно."


def get_fixtures(league_identifier):
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return f"Няма лига с име/ID '{league_identifier}'."
    rows = matches_repo.get_by_league(lid)
    if not rows:
        return "Няма насрочени мачове."
    out = []
    for r in rows:
        out.append(f"{r['match_date']}: {r['home_name']} vs {r['away_name']} ({r['home_goals']}-{r['away_goals']})")
    return "\n".join(out)
