#!/usr/bin/env python3
import os
import sys
import unittest

# ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Ensure tests directory is on path so test helpers (test_config) can be imported
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config, create_test_clubs
from src.services.leagues_service import create_league, add_club_to_league, generate_round_robin, get_fixtures
from src.db import execute_query


class TestLeaguesService(unittest.TestCase):
    def setUp(self):
        test_config.setup_test_environment()
        create_test_clubs()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def test_create_league_and_add_teams_and_generate(self):
        res = create_league('Българска Първа Лига', '2025/26')
        self.assertIn('създад', res.lower())

        # add clubs
        clubs = execute_query('SELECT id FROM clubs LIMIT 4', fetch=True)
        self.assertTrue(len(clubs) >= 4)
        league_row = execute_query("SELECT id FROM leagues WHERE name = ?", ('Българска Първа Лига',), fetch=True)
        lid = league_row[0]['id']
        for c in clubs:
            add_club_to_league(lid, c['id'])

        # generate fixtures
        res2 = generate_round_robin(lid)
        self.assertIn('създад', res2.lower())

        # check matches count: n*(n-1)/2
        n = len(clubs)
        expected = n * (n - 1) // 2
        rows = execute_query('SELECT COUNT(*) as count FROM matches WHERE league_id = ?', (lid,), fetch=True)
        self.assertEqual(rows[0]['count'], expected)


if __name__ == '__main__':
    unittest.main()
