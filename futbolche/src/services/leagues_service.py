from datetime import date, timedelta, datetime
from db import execute, fetch_all, fetch_one


def create_league(name: str, season: str):
    if not name or not name.strip():
        return "Името на лигата не може да бъде празно."

    res = execute("INSERT INTO leagues (name, season) VALUES (?, ?)", (name.strip(), season.strip()))
    if res is None:
        return "Грешка при създаване на лига."
    return f"Лига '{name}' ({season}) беше създадена успешно."


def add_club_to_league(league_identifier, club_identifier):
    # resolve league id
    lid = None
    if isinstance(league_identifier, int) or str(league_identifier).isdigit():
        lid = int(league_identifier)
    else:
        row = fetch_one("SELECT id FROM leagues WHERE LOWER(name)=LOWER(?)", (league_identifier,))
        if row:
            lid = row['id']

    if not lid:
        return "Лигата не съществува."

    # resolve club id
    cid = None
    if isinstance(club_identifier, int) or str(club_identifier).isdigit():
        cid = int(club_identifier)
    else:
        row = fetch_one("SELECT id FROM clubs WHERE LOWER(name)=LOWER(?)", (club_identifier,))
        if row:
            cid = row['id']

    if not cid:
        return "Клубът не съществува."

    res = execute("INSERT INTO league_teams (league_id, club_id) VALUES (?, ?)", (lid, cid))
    if res is None:
        return "Грешка при добавяне на клуба в лигата (възможно дублиране)."
    return "Клубът беше добавен в лигата успешно."


def get_league_teams(league_identifier):
    # resolve league id
    lid = None
    if isinstance(league_identifier, int) or str(league_identifier).isdigit():
        lid = int(league_identifier)
    else:
        row = fetch_one("SELECT id FROM leagues WHERE LOWER(name)=LOWER(?)", (league_identifier,))
        if row:
            lid = row['id']

    if not lid:
        return []

    rows = fetch_all("SELECT c.* FROM clubs c JOIN league_teams lt ON c.id = lt.club_id WHERE lt.league_id = ? ORDER BY c.name", (lid,))
    return rows or []


def generate_round_robin(league_identifier, double_round: bool = False, start_date: str = None, interval_days: int = 7):
    """Generate round-robin fixtures for a league.

    - `double_round`: if True, generate home+away legs (double round-robin).
    - `start_date`: ISO date string for first match day; defaults to today.
    - `interval_days`: days between matchdays.
    """
    teams = get_league_teams(league_identifier)
    if not teams or len(teams) < 2:
        return "Недостатъчно отбори за създаване на кръгове."

    # get league id
    if isinstance(league_identifier, int) or str(league_identifier).isdigit():
        lid = int(league_identifier)
    else:
        row = fetch_one("SELECT id FROM leagues WHERE LOWER(name)=LOWER(?)", (league_identifier,))
        lid = row['id'] if row else None

    if not lid:
        return "Лигата не съществува."

    club_ids = [t['id'] for t in teams]

    # schedule dates
    if start_date:
        try:
            current = datetime.strptime(start_date, "%Y-%m-%d").date()
        except Exception:
            current = date.today()
    else:
        current = date.today()

    created = 0

    # Single round-robin: each pair once (i home, j away)
    for i in range(len(club_ids)):
        for j in range(i + 1, len(club_ids)):
            res = execute(
                "INSERT INTO matches (home_team_id, away_team_id, match_date, league_id) VALUES (?, ?, ?, ?)",
                (club_ids[i], club_ids[j], current.isoformat(), lid)
            )
            if res:
                created += 1
            current = current + timedelta(days=interval_days)

    # Double round-robin: add reverse fixtures
    if double_round:
        for i in range(len(club_ids)):
            for j in range(i + 1, len(club_ids)):
                res = execute(
                    "INSERT INTO matches (home_team_id, away_team_id, match_date, league_id) VALUES (?, ?, ?, ?)",
                    (club_ids[j], club_ids[i], current.isoformat(), lid)
                )
                if res:
                    created += 1
                current = current + timedelta(days=interval_days)

    return f"Създадени {created} мача за лига {league_identifier}."


def get_standings(league_identifier):
    """Compute standings for a league: played, won, draw, lost, goals for/against, goal diff, points."""
    # resolve league id
    lid = None
    if isinstance(league_identifier, int) or str(league_identifier).isdigit():
        lid = int(league_identifier)
    else:
        row = fetch_one("SELECT id FROM leagues WHERE LOWER(name)=LOWER(?)", (league_identifier,))
        if row:
            lid = row['id']

    if not lid:
        return "Лигата не съществува."

    rows = fetch_all(
        "SELECT m.*, hc.name as home_name, ac.name as away_name FROM matches m JOIN clubs hc ON m.home_team_id = hc.id JOIN clubs ac ON m.away_team_id = ac.id WHERE m.league_id = ?",
        (lid,)
    )

    if not rows:
        return "Няма мачове в тази лига."

    table = {}
    def ensure(team_name):
        if team_name not in table:
            table[team_name] = {'P':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'GD':0, 'Pts':0}

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

    # finalize GD and sort
    out = []
    for team, stats in table.items():
        stats['GD'] = stats['GF'] - stats['GA']
        out.append((team, stats))

    out.sort(key=lambda x: (-x[1]['Pts'], -x[1]['GD'], -x[1]['GF'], x[0]))

    lines = []
    for pos, (team, s) in enumerate(out, start=1):
        lines.append(f"{pos}. {team} | P:{s['P']} W:{s['W']} D:{s['D']} L:{s['L']} GF:{s['GF']} GA:{s['GA']} GD:{s['GD']} Pts:{s['Pts']}")

    return "\n".join(lines)


def get_fixtures(league_identifier):
    # resolve league id
    lid = None
    if isinstance(league_identifier, int) or str(league_identifier).isdigit():
        lid = int(league_identifier)
    else:
        row = fetch_one("SELECT id FROM leagues WHERE LOWER(name)=LOWER(?)", (league_identifier,))
        if row:
            lid = row['id']

    if not lid:
        return "Лигата не съществува."

    rows = fetch_all(
        "SELECT m.*, hc.name as home_name, ac.name as away_name FROM matches m JOIN clubs hc ON m.home_team_id = hc.id JOIN clubs ac ON m.away_team_id = ac.id WHERE m.league_id = ? ORDER BY m.match_date",
        (lid,)
    )

    if not rows:
        return "Няма насрочени мачове."

    out = []
    for r in rows:
        out.append(f"{r['match_date']}: {r['home_name']} vs {r['away_name']} ({r['home_goals']}-{r['away_goals']})")

    return "\n".join(out)
