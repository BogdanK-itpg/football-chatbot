from typing import List, Dict, Optional
from repositories import standings_repo
from utils.logger import log_command


AUTO_MARK_PLAYED = True


def calculate_standings(league_name: str, season: Optional[str] = None) -> List[Dict]:
    if str(league_name).isdigit():
        league = standings_repo.get_league_by_id(int(league_name))
    elif season:
        league = standings_repo.get_league_by_name_and_season(league_name, season)
    else:
        league = standings_repo.get_league_by_name(league_name)
    if not league:
        return []

    league_id = league['id']
    teams = standings_repo.get_league_teams(league_id)
    if not teams:
        return []

    team_map = {t['id']: t['name'] for t in teams}

    stats = {}
    for t in teams:
        stats[t['id']] = {
            'team_id': t['id'],
            'team': t['name'],
            'mp': 0,
            'w': 0,
            'd': 0,
            'l': 0,
            'gf': 0,
            'ga': 0,
            'gd': 0,
            'pts': 0
        }

    invalid_teams = standings_repo.validate_match_consistency(league_id)
    if invalid_teams:
        for row in invalid_teams:
            log_command(
                f"standings: league={league_name}",
                "standings_warning",
                "WARNING",
                f"Match references team not registered in league (match_id={row['id']})",
                {'league_id': str(league_id), 'match_id': str(row['id'])}
            )

    matches = standings_repo.get_played_matches(league_id)

    if AUTO_MARK_PLAYED:
        extra = standings_repo.get_matches_with_scores_not_played(league_id)
        matches.extend(extra)

    for m in matches:
        home_id = m['home_team_id']
        away_id = m['away_team_id']

        if home_id not in team_map or away_id not in team_map:
            log_command(
                f"standings: league={league_name}",
                "standings_warning",
                "WARNING",
                f"Match references team not registered in league (match_id={m['id']})",
                {'league_id': str(league_id), 'match_id': str(m['id'])}
            )
            continue

        hg = int(m['home_goals'])
        ag = int(m['away_goals'])

        stats[home_id]['mp'] += 1
        stats[away_id]['mp'] += 1
        stats[home_id]['gf'] += hg
        stats[home_id]['ga'] += ag
        stats[away_id]['gf'] += ag
        stats[away_id]['ga'] += hg

        if hg > ag:
            stats[home_id]['w'] += 1
            stats[away_id]['l'] += 1
            stats[home_id]['pts'] += 3
        elif hg < ag:
            stats[away_id]['w'] += 1
            stats[home_id]['l'] += 1
            stats[away_id]['pts'] += 3
        else:
            stats[home_id]['d'] += 1
            stats[away_id]['d'] += 1
            stats[home_id]['pts'] += 1
            stats[away_id]['pts'] += 1

    for sid in stats:
        stats[sid]['gd'] = stats[sid]['gf'] - stats[sid]['ga']

    standings_list = sorted(stats.values(), key=lambda x: (-x['pts'], -x['gd'], -x['gf'], x['team']))

    _apply_head_to_head(standings_list, matches, team_map)

    for pos, entry in enumerate(standings_list, start=1):
        entry['position'] = pos

    return standings_list


def _apply_head_to_head(standings_list: List[Dict], matches: List, team_map: Dict[int, str]) -> None:
    i = 0
    while i < len(standings_list):
        tied_group = [standings_list[i]]
        j = i + 1
        while j < len(standings_list):
            if (standings_list[j]['pts'] == tied_group[0]['pts']
                    and standings_list[j]['gd'] == tied_group[0]['gd']
                    and standings_list[j]['gf'] == tied_group[0]['gf']):
                tied_group.append(standings_list[j])
                j += 1
            else:
                break

        if len(tied_group) > 1:
            team_ids = [e['team_id'] for e in tied_group]
            h2h = {tid: {'pts': 0, 'gd': 0, 'gf': 0} for tid in team_ids}

            for m in matches:
                home_id = m['home_team_id']
                away_id = m['away_team_id']
                if home_id in team_ids and away_id in team_ids:
                    hg = int(m['home_goals'])
                    ag = int(m['away_goals'])

                    h2h[home_id]['gf'] += hg
                    h2h[home_id]['gd'] += (hg - ag)
                    h2h[away_id]['gf'] += ag
                    h2h[away_id]['gd'] += (ag - hg)

                    if hg > ag:
                        h2h[home_id]['pts'] += 3
                    elif hg < ag:
                        h2h[away_id]['pts'] += 3
                    else:
                        h2h[home_id]['pts'] += 1
                        h2h[away_id]['pts'] += 1

            tied_group.sort(key=lambda e: (
                -h2h[e['team_id']]['pts'],
                -h2h[e['team_id']]['gd'],
                -h2h[e['team_id']]['gf'],
                e['team']
            ))

            standings_list[i:j] = tied_group

        i = j
