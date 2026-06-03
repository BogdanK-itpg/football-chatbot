from datetime import date, timedelta, datetime
from repositories import leagues_repo, clubs_repo, matches_repo


def create_league(name: str, season: str):
    if not name or not name.strip():
        return "Името на лигата не може да бъде празно."
    res = leagues_repo.create(name.strip(), season.strip())
    if res is None:
        return "Грешка при създаване на лига."
    return f"Лига '{name}' ({season}) беше създадена успешно."


def add_club_to_league(league_identifier, club_identifier):
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


def generate_round_robin(league_identifier, double_round: bool = False, start_date: str = None, interval_days: int = 7):
    teams = get_league_teams(league_identifier)
    if not teams or len(teams) < 2:
        return "Недостатъчно отбори за създаване на кръгове."
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return "Лигата не съществува."
    club_ids = [t['id'] for t in teams]

    if start_date:
        try:
            current = datetime.strptime(start_date, "%Y-%m-%d").date()
        except Exception:
            current = date.today()
    else:
        current = date.today()

    created = 0
    round_no = 1
    for i in range(len(club_ids)):
        for j in range(i + 1, len(club_ids)):
            res = matches_repo.create(club_ids[i], club_ids[j], current.isoformat(), league_id=lid, round_no=round_no)
            if res:
                created += 1
            current = current + timedelta(days=interval_days)
        round_no += 1

    if double_round:
        for i in range(len(club_ids)):
            for j in range(i + 1, len(club_ids)):
                res = matches_repo.create(club_ids[j], club_ids[i], current.isoformat(), league_id=lid, round_no=round_no)
                if res:
                    created += 1
                current = current + timedelta(days=interval_days)
            round_no += 1

    return f"Създадени {created} мача за лига {league_identifier}."


def get_standings(league_identifier):
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return "Лигата не съществува."
    rows = matches_repo.get_by_league(lid)
    if not rows:
        return "Няма мачове в тази лига."
    table = {}

    def ensure(team_name):
        if team_name not in table:
            table[team_name] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}

    for r in rows:
        home = r['home_name']
        away = r['away_name']
        ensure(home)
        ensure(away)
        hg = r['home_goals'] if r['home_goals'] is not None else 0
        ag = r['away_goals'] if r['away_goals'] is not None else 0
        table[home]['P'] += 1
        table[away]['P'] += 1
        table[home]['GF'] += hg
        table[home]['GA'] += ag
        table[away]['GF'] += ag
        table[away]['GA'] += hg
        if hg > ag:
            table[home]['W'] += 1
            table[away]['L'] += 1
            table[home]['Pts'] += 3
        elif hg < ag:
            table[away]['W'] += 1
            table[home]['L'] += 1
            table[away]['Pts'] += 3
        else:
            table[home]['D'] += 1
            table[away]['D'] += 1
            table[home]['Pts'] += 1
            table[away]['Pts'] += 1

    out = []
    for team, stats in table.items():
        stats['GD'] = stats['GF'] - stats['GA']
        out.append((team, stats))
    out.sort(key=lambda x: (-x[1]['Pts'], -x[1]['GD'], -x[1]['GF'], x[0]))

    lines = []
    for pos, (team, s) in enumerate(out, start=1):
        lines.append(
            f"{pos}. {team} | P:{s['P']} W:{s['W']} D:{s['D']} L:{s['L']} "
            f"GF:{s['GF']} GA:{s['GA']} GD:{s['GD']} Pts:{s['Pts']}"
        )
    return "\n".join(lines)


def get_fixtures(league_identifier):
    lid = leagues_repo.resolve_id(league_identifier)
    if not lid:
        return "Лигата не съществува."
    rows = matches_repo.get_by_league(lid)
    if not rows:
        return "Няма насрочени мачове."
    out = []
    for r in rows:
        out.append(f"{r['match_date']}: {r['home_name']} vs {r['away_name']} ({r['home_goals']}-{r['away_goals']})")
    return "\n".join(out)
