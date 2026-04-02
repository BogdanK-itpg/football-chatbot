#!/usr/bin/env python3
"""Unit tests for match events recording and standings computation"""

import os
import sys
import unittest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from services import matches_service as matches
from services import leagues_service as leagues
from services import players_service as players
from db import fetch_one, fetch_all


class TestMatchesEvents(unittest.TestCase):
    def setUp(self):
        test_config.setup_test_environment()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def test_record_event_updates_match_and_saves_event(self):
        # create a fixture match with no score
        res = matches.record_match('Левски София', 'ЦСКА София', '2025-09-10', home_goals=0, away_goals=0)
        # find created match id
        row = fetch_one("SELECT id FROM matches WHERE match_date = ? AND home_team_id = (SELECT id FROM clubs WHERE name = ?) AND away_team_id = (SELECT id FROM clubs WHERE name = ?)", ('2025-09-10','Левски София','ЦСКА София'))
        self.assertIsNotNone(row)
        mid = row['id']

        # ensure initial goals are null or 0
        m_before = matches.get_match(mid)
        self.assertIsNotNone(m_before)

        # record a goal for a Levski player
        # find player id for Иван Иванов (Levski)
        pid = players.get_player_id('Иван Иванов')
        self.assertIsNotNone(pid)

        r = matches.record_event(mid, 'Иван Иванов', 'goal', 23)
        self.assertIn('успешно', r.lower())

        # verify match goals incremented
        m_after = matches.get_match(mid)
        self.assertIsNotNone(m_after)
        # if Levski was home, home_goals should be 1
        self.assertEqual(m_after['home_goals'], 1)

        # verify event listed
        events = matches.get_match_events(mid)
        self.assertIn("goal", events)
        self.assertIn('Иван Иванов', events)

    def test_get_league_standings_computes_order(self):
        # create a league and add three clubs
        leagues.create_league('Test League', '2025')
        lid_row = fetch_one("SELECT id FROM leagues WHERE name = ?", ('Test League',))
        self.assertIsNotNone(lid_row)
        lid = lid_row['id']

        # add three clubs to league
        leagues.add_club_to_league(lid, 'Левски София')
        leagues.add_club_to_league(lid, 'ЦСКА София')
        leagues.add_club_to_league(lid, 'Ботев Пловдив')

        # create matches with results
        matches.record_match('Левски София', 'ЦСКА София', '2025-09-01', home_goals=2, away_goals=1, league_id=lid)
        matches.record_match('ЦСКА София', 'Ботев Пловдив', '2025-09-02', home_goals=0, away_goals=1, league_id=lid)
        matches.record_match('Ботев Пловдив', 'Левски София', '2025-09-03', home_goals=0, away_goals=0, league_id=lid)

        standings = matches.get_league_standings(lid)
        self.assertIsInstance(standings, str)
        # Levski should be top with 4 points (win + draw)
        self.assertIn('Левски София', standings)
        self.assertIn('Pts:4', standings)


if __name__ == '__main__':
    unittest.main()
