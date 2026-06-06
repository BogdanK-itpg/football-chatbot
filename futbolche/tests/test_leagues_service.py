#!/usr/bin/env python3
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config, create_test_clubs
from services.leagues_service import (
    create_league,
    add_club_to_league,
    remove_club_from_league,
    generate_round_robin,
    get_fixtures,
    get_standings,
)
from repositories import leagues_repo, matches_repo
from db import execute_query, fetch_one


class TestLeaguesService(unittest.TestCase):
    def setUp(self):
        test_config.setup_test_environment()
        create_test_clubs()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def _create_league_with_teams(self, name="Тестова Лига", season="2025", team_count=4):
        create_league(name, season)
        lid = leagues_repo.resolve_id(name)
        clubs = execute_query(f'SELECT id FROM clubs LIMIT {team_count}', fetch=True)
        for c in clubs:
            add_club_to_league(lid, c['id'])
        return lid

    # ---- Create League ----
    def test_create_league_ok(self):
        res = create_league('Българска Първа Лига', '2025/26')
        self.assertIn('създадена', res.lower())

    def test_create_league_duplicate_error(self):
        create_league('Българска Първа Лига', '2025/26')
        res = create_league('Българска Първа Лига', '2025/26')
        self.assertIn('вече съществува', res.lower())

    def test_create_league_empty_name_error(self):
        res = create_league('', '2025')
        self.assertIn('празно', res.lower())

    def test_create_league_invalid_season_format(self):
        res = create_league('Лига', 'abc')
        self.assertIn('формат', res.lower())

    def test_create_league_missing_season(self):
        res = create_league('Лига', '')
        self.assertIn('празен', res.lower())

    # ---- Add Team to League ----
    def test_add_team_ok(self):
        create_league('Тест', '2025')
        lid = leagues_repo.resolve_id('Тест')
        clubs = execute_query('SELECT id FROM clubs LIMIT 1', fetch=True)
        res = add_club_to_league(lid, clubs[0]['id'])
        self.assertIn('добавен', res.lower())

    def test_add_team_duplicate_error(self):
        create_league('Тест', '2025')
        lid = leagues_repo.resolve_id('Тест')
        clubs = execute_query('SELECT id FROM clubs LIMIT 1', fetch=True)
        cid = clubs[0]['id']
        add_club_to_league(lid, cid)
        res = add_club_to_league(lid, cid)
        self.assertIn('дублиране', res.lower())

    def test_add_team_nonexistent_club(self):
        create_league('Тест', '2025')
        lid = leagues_repo.resolve_id('Тест')
        res = add_club_to_league(lid, 99999)
        self.assertIn('не съществува', res.lower())

    # ---- Remove Team from League ----
    def test_remove_team_ok(self):
        create_league('Тест', '2025')
        lid = leagues_repo.resolve_id('Тест')
        clubs = execute_query('SELECT id FROM clubs LIMIT 1', fetch=True)
        cid = clubs[0]['id']
        add_club_to_league(lid, cid)
        res = remove_club_from_league(lid, cid)
        self.assertIn('премахнат', res.lower())
        teams = leagues_repo.get_teams(lid)
        self.assertFalse(any(t['id'] == cid for t in teams))

    def test_remove_team_blocked_after_schedule(self):
        lid = self._create_league_with_teams("Блокирана", "2025", 4)
        generate_round_robin(lid)
        clubs = execute_query('SELECT id FROM clubs LIMIT 1', fetch=True)
        cid = clubs[0]['id']
        res = remove_club_from_league(lid, cid)
        self.assertIn('програмата', res.lower())

    def test_remove_team_not_in_league(self):
        create_league('Тест', '2025')
        lid = leagues_repo.resolve_id('Тест')
        clubs = execute_query('SELECT id FROM clubs LIMIT 1', fetch=True)
        cid = clubs[0]['id']
        res = remove_club_from_league(lid, cid)
        self.assertIn('не е в тази лига', res.lower())

    # ---- Generate Schedule (Round-Robin) ----
    def test_generate_schedule_even_teams(self):
        lid = self._create_league_with_teams("Четна", "2025", 4)
        res = generate_round_robin(lid)
        self.assertIn('създадени', res.lower())
        rows = matches_repo.get_by_league(lid)
        self.assertEqual(len(rows), 6)  # 4*3/2 = 6
        rounds = set(r['round_no'] for r in rows)
        self.assertEqual(len(rounds), 3)  # N-1 = 3 rounds
        for rnd in range(1, 4):
            rnd_matches = [r for r in rows if r['round_no'] == rnd]
            self.assertEqual(len(rnd_matches), 2)  # N/2 = 2 per round

    def test_generate_schedule_odd_teams_with_bye(self):
        lid = self._create_league_with_teams("Нечетна", "2025", 3)
        res = generate_round_robin(lid)
        self.assertIn('създадени', res.lower())
        rows = matches_repo.get_by_league(lid)
        self.assertEqual(len(rows), 3)  # 3*2/2 = 3
        rounds = set(r['round_no'] for r in rows)
        self.assertEqual(len(rounds), 3)  # N = 3 rounds (with BYE)

    def test_generate_schedule_too_few_teams(self):
        create_league('Празна', '2025')
        lid = leagues_repo.resolve_id('Празна')
        res = generate_round_robin(lid)
        self.assertIn('недостатъчно', res.lower())

    def test_generate_schedule_regenerate_blocked(self):
        lid = self._create_league_with_teams("Двойна", "2025", 4)
        generate_round_robin(lid)
        res = generate_round_robin(lid)
        self.assertIn('вече е генерирана', res.lower())

    # ---- Standings ----
    def test_get_standings_ok(self):
        lid = self._create_league_with_teams("Класиране", "2025", 4)
        generate_round_robin(lid)
        res = get_standings(lid)
        self.assertIsInstance(res, str)
        # Should contain team names since standings uses
        # the joined query with home_name/away_name
        self.assertTrue(len(res) > 0)

    # ---- Fixtures ----
    def test_get_fixtures_ok(self):
        lid = self._create_league_with_teams("Мачове", "2025", 4)
        generate_round_robin(lid)
        res = get_fixtures(lid)
        self.assertIsInstance(res, str)
        self.assertIn('vs', res)

    # ---- Self-match prevention ----
    def test_self_match_prevented_in_repo(self):
        from repositories.matches_repo import create
        res = create(1, 1, '2025-01-01')
        self.assertIsNone(res)


if __name__ == '__main__':
    unittest.main()
