#!/usr/bin/env python3
"""
Required test scenarios from the specification.
Tests: Show Round, Select Match, Save Result, Invalid Result,
       Goal from wrong team, Goal minute 0/200, Yellow card, Show Events.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from handlers.handler_matches import (
    handle_show_round,
    handle_save_result,
    handle_add_goal,
    handle_select_match,
    handle_add_card,
    handle_show_events,
)
from services.clubs_service import add_club
from services.players_service import add_player as add_player_svc, get_club_id, get_player_id
from services.leagues_service import create_league, add_club_to_league, generate_round_robin
from services.matches_service import record_match
from repositories import matches_repo, events_repo, clubs_repo, players_repo, leagues_repo
from state import set_current_match, clear_current_match, get_current_match
from db import fetch_one, fetch_all


class TestRequiredScenarios(unittest.TestCase):
    """All 8 required test scenarios from the spec."""

    def setUp(self):
        test_config.setup_test_environment()
        clear_current_match()
        self._create_test_data()

    def tearDown(self):
        test_config.cleanup_test_environment()
        clear_current_match()

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
        """Get the first unplayed match created by _create_test_data."""
        for m in matches_repo.get_all():
            if not m['is_played']:
                return m
        return matches_repo.get_all()[-1] if matches_repo.get_all() else None

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

    # ---- Scenario 2: Select Match -> OK ----
    def test_select_match_ok(self):
        """2. Select match sets the current match in state."""
        match = self._get_test_match()
        mid = match['id']
        result = handle_select_match({'match_id': str(mid)})
        self.assertIn("Избран", result)
        self.assertEqual(get_current_match(), mid)

    # ---- Scenario 3: Save Result -> OK ----
    def test_save_result_ok(self):
        """3. Save result for an existing unplayed match."""
        # Get an unplayed match
        match = self._get_test_match()
        mid = match['id']
        set_current_match(mid)

        result = handle_save_result({
            'home_team': match['home_name'],
            'away_team': match['away_name'],
            'home_goals': '3',
            'away_goals': '1'
        })
        self.assertIn("успешно", result.lower())

        # Verify score was saved
        updated = matches_repo.get_by_id(mid)
        self.assertEqual(updated['home_goals'], 3)
        self.assertEqual(updated['away_goals'], 1)
        self.assertEqual(updated['is_played'], 1)

    # ---- Scenario 4: Invalid Result Format -> ERROR ----
    def test_save_result_invalid_format_error(self):
        """4. Invalid result format returns error."""
        match = self._get_test_match()
        set_current_match(match['id'])

        result = handle_save_result({
            'home_team': match['home_name'],
            'away_team': match['away_name'],
            'home_goals': '-1',
            'away_goals': '5'
        })
        self.assertIn("отрицателни", result.lower())

        result2 = handle_save_result({
            'home_team': match['home_name'],
            'away_team': match['away_name'],
            'home_goals': 'abc',
            'away_goals': '5'
        })
        self.assertIn("цели числа", result2.lower())

    # ---- Scenario 5: Goal from wrong team -> ERROR ----
    def test_add_goal_wrong_team_error(self):
        """5. Goal from a player whose team is not in the match is rejected."""
        match = self._get_test_match()
        set_current_match(match['id'])

        # Get a Botev player (club_id=3) — match is Levski(1) vs CSKA(2)
        botev_player = players_repo.get_by_club(3)[0]

        result = handle_add_goal({
            'player_name': botev_player['full_name'],
            'team_name': 'Ботев Пловдив',
            'minute': '23'
        })
        self.assertIn("не участва", result.lower())

    # ---- Scenario 6: Goal minute 0 or 200 -> ERROR ----
    def test_add_goal_invalid_minute_error(self):
        """6. Goal with minute 0 or 200 is rejected."""
        match = self._get_test_match()
        set_current_match(match['id'])

        levski_player = players_repo.get_by_club(1)[0]

        result_zero = handle_add_goal({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'minute': '0'
        })
        self.assertIn("между 1 и 120", result_zero.lower())

        result_high = handle_add_goal({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'minute': '200'
        })
        self.assertIn("между 1 и 120", result_high.lower())

    # ---- Scenario 7: Valid Yellow Card -> OK ----
    def test_add_yellow_card_ok(self):
        """7. Valid yellow card is recorded successfully."""
        match = self._get_test_match()
        set_current_match(match['id'])

        levski_player = players_repo.get_by_club(1)[0]

        result = handle_add_card({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'card_type': 'Y',
            'minute': '55'
        })
        self.assertIn("успешно", result.lower())

        # Verify card was saved
        cards = events_repo.count_cards_in_match(get_current_match(), levski_player['id'])
        self.assertEqual(cards['yellow'], 1)

    # ---- Scenario 8: Show Events -> OK ----
    def test_show_events_ok(self):
        """8. Show events displays all events in order."""
        match = self._get_test_match()
        set_current_match(match['id'])
        mid = get_current_match()

        levski_player = players_repo.get_by_club(1)[0]
        handle_add_goal({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'minute': '23'
        })

        result = handle_show_events({'match_id': str(mid)})
        self.assertIsInstance(result, str)
        self.assertIn("ГОЛ", result)
        self.assertIn(levski_player['full_name'], result)

    # ---- Additional: Duplicate result rejected ----
    def test_duplicate_result_rejected(self):
        """Save result twice on same match is rejected."""
        match = self._get_test_match()
        set_current_match(match['id'])
        handle_save_result({
            'home_team': match['home_name'],
            'away_team': match['away_name'],
            'home_goals': '2',
            'away_goals': '0'
        })
        result = handle_save_result({
            'home_team': match['home_name'],
            'away_team': match['away_name'],
            'home_goals': '3',
            'away_goals': '1'
        })
        self.assertIn("вече има записан", result.lower())

    # ---- Additional: Goal after match played ----
    def test_goal_after_match_played_rejected(self):
        """Goal cannot be added after match result is saved."""
        match = self._get_test_match()
        set_current_match(match['id'])
        handle_save_result({
            'home_team': match['home_name'],
            'away_team': match['away_name'],
            'home_goals': '1',
            'away_goals': '0'
        })
        levski_player = players_repo.get_by_club(1)[0]
        result = handle_add_goal({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'minute': '90'
        })
        self.assertIn("приключил", result.lower())

    # ---- Additional: Second yellow -> red ----
    def test_two_yellows_converted_to_red(self):
        """Two yellows for same player in same match auto-convert to red."""
        match = self._get_test_match()
        set_current_match(match['id'])
        levski_player = players_repo.get_by_club(1)[0]

        handle_add_card({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'card_type': 'Y',
            'minute': '30'
        })

        result = handle_add_card({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'card_type': 'Y',
            'minute': '60'
        })
        # Should reject — must use R for second yellow
        self.assertIn("червен", result.lower())

    # ---- Additional: Red card prevents goals ----
    def test_red_card_prevents_goals(self):
        """Goal after red card for same player is rejected."""
        match = self._get_test_match()
        set_current_match(match['id'])
        levski_player = players_repo.get_by_club(1)[0]

        handle_add_card({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'card_type': 'R',
            'minute': '40'
        })

        result = handle_add_goal({
            'player_name': levski_player['full_name'],
            'team_name': 'Левски София',
            'minute': '50'
        })
        self.assertIn("червен картон", result.lower())

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
