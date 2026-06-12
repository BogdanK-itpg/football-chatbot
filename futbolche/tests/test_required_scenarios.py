#!/usr/bin/env python3
"""Required test scenarios that remain supported by the current spec."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from handlers.handler_matches import (
    handle_show_round,
    handle_show_events,
)
from services.clubs_service import add_club
from services.players_service import add_player as add_player_svc
from services.leagues_service import create_league, add_club_to_league
from services.matches_service import record_match, record_event
from repositories import matches_repo, players_repo, leagues_repo


class TestRequiredScenarios(unittest.TestCase):
    """Regression tests for supported round/event match flows."""

    def setUp(self):
        test_config.setup_test_environment()
        self._create_test_data()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def _create_test_data(self):
        """Create clubs, players, league, and matches for testing."""
        add_club("Левски София")
        add_club("ЦСКА София")
        add_club("Ботев Пловдив")

        add_player_svc(1, "Иван Иванов", "1995-03-15", "България", "FW", 9, "Активен")
        add_player_svc(1, "Петър Петров", "1998-07-22", "България", "DF", 4, "Активен")
        add_player_svc(2, "Георги Димитров", "1994-05-12", "България", "GK", 1, "Активен")
        add_player_svc(2, "Димитър Иванов", "1997-12-25", "България", "MF", 8, "Активен")

        create_league("Първа Лига", "2025")
        lid = leagues_repo.resolve_id("Първа Лига")
        add_club_to_league(lid, "Левски София")
        add_club_to_league(lid, "ЦСКА София")
        add_club_to_league(lid, "Ботев Пловдив")

        # Create matches with round numbers (no goals = unplayed)
        record_match("Левски София", "ЦСКА София", "2025-08-01", league_id=lid, round_no=1)
        record_match("Ботев Пловдив", "Левски София", "2025-08-08", league_id=lid, round_no=2)
        record_match("ЦСКА София", "Ботев Пловдив", "2025-08-15", league_id=lid, round_no=2)

        self.league_id = lid

    def _get_test_match(self):
        """Get the first match created by _create_test_data."""
        all_matches = matches_repo.get_all()
        return all_matches[0] if all_matches else None

    # ---- Scenario 1: Show Round -> OK ----
    def test_show_round_ok(self):
        """1. Show round returns matches for a given round."""
        result = handle_show_round({
            'round_no': '1',
            'league_name': 'Първа Лига',
            'season': '2025'
        })
        self.assertIsInstance(result, str)
        self.assertIn("Кръг 1", result)
        self.assertIn("Левски София", result)
        self.assertIn("ЦСКА София", result)
        self.assertIn("ID:", result)

    # ---- Scenario 2: Show Events -> OK ----
    def test_show_events_ok(self):
        """Show events displays recorded events in order."""
        match = self._get_test_match()
        mid = match['id']

        levski_player = players_repo.get_by_club(1)[0]
        record_event(mid, levski_player['id'], levski_player['club_id'], 'goal', minute=23)

        result = handle_show_events({'match_id': str(mid)})
        self.assertIsInstance(result, str)
        self.assertIn("ГОЛ", result)
        self.assertIn(levski_player['full_name'], result)

    # ---- Additional: NLU pattern for record_match is fixed ----
    def test_record_match_nlu_pattern_fixed(self):
        """The previously broken 'запиши мач ... резултат ...' pattern now works."""
        from chatbot.nlu import parse_input

        intent, params = parse_input("запиши мач Левски София срещу ЦСКА София дата 2025-09-01 резултат 2-1")
        self.assertEqual(intent, "record_match")
        self.assertIsNotNone(params)
        self.assertIn("home_team", params)
        self.assertIn("away_team", params)
        self.assertIn("home_goals", params)
        self.assertIn("away_goals", params)


if __name__ == '__main__':
    unittest.main()
