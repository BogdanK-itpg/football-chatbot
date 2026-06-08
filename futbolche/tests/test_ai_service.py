#!/usr/bin/env python3
"""Tests for AI prediction module."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from ai import ai_service
from repositories import leagues_repo
from services.matches_service import record_match


class TestAIService(unittest.TestCase):

    def setUp(self):
        test_config.setup_test_environment()
        self._create_full_data()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def _create_full_data(self):
        from services.clubs_service import add_club
        for name in ["Левски София", "ЦСКА София", "Ботев Пловдив", "Лудогорец Разград"]:
            add_club(name)

        from services.leagues_service import create_league, add_club_to_league
        create_league("Първа Лига", "2025/2026")
        lid = leagues_repo.resolve_id("Първа Лига")
        for name in ["Левски София", "ЦСКА София", "Ботев Пловдив", "Лудогорец Разград"]:
            add_club_to_league(lid, name)

        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=2, away_goals=1, league_id=lid)
        record_match("Ботев Пловдив", "Лудогорец Разград", "2025-08-01",
                     home_goals=1, away_goals=1, league_id=lid)
        record_match("Левски София", "Ботев Пловдив", "2025-08-08",
                     home_goals=3, away_goals=1, league_id=lid)
        record_match("ЦСКА София", "Лудогорец Разград", "2025-08-08",
                     home_goals=0, away_goals=2, league_id=lid)
        record_match("Левски София", "Лудогорец Разград", "2025-08-15",
                     home_goals=1, away_goals=0, league_id=lid)
        record_match("ЦСКА София", "Левски София", "2025-08-15",
                     home_goals=0, away_goals=2, league_id=lid)
        record_match("Лудогорец Разград", "Ботев Пловдив", "2025-08-22",
                     home_goals=3, away_goals=0, league_id=lid)
        record_match("Левски София", "Ботев Пловдив", "2025-08-29",
                     home_goals=1, away_goals=1, league_id=lid)
        record_match("Лудогорец Разград", "Левски София", "2025-09-05",
                     home_goals=2, away_goals=1, league_id=lid)
        record_match("ЦСКА София", "Ботев Пловдив", "2025-08-29",
                     home_goals=2, away_goals=0, league_id=lid)
        record_match("Лудогорец Разград", "ЦСКА София", "2025-09-05",
                     home_goals=1, away_goals=1, league_id=lid)
        record_match("ЦСКА София", "Ботев Пловдив", "2025-09-12",
                     home_goals=3, away_goals=2, league_id=lid)
        record_match("Ботев Пловдив", "Лудогорец Разград", "2025-09-12",
                     home_goals=0, away_goals=2, league_id=lid)
        record_match("Лудогорец Разград", "ЦСКА София", "2025-09-19",
                     home_goals=2, away_goals=0, league_id=lid)

    def test_valid_prediction(self):
        result = ai_service.predict_match("Левски София", "Лудогорец Разград")
        self.assertIn('home', result)
        self.assertIn('draw', result)
        self.assertIn('away', result)
        for key in ('home', 'draw', 'away'):
            self.assertIsInstance(result[key], int)

    def test_sum_equals_100(self):
        result = ai_service.predict_match("Левски София", "Лудогорец Разград")
        total = result['home'] + result['draw'] + result['away']
        self.assertEqual(total, 100)

    def test_invalid_team(self):
        with self.assertRaises(ValueError) as ctx:
            ai_service.predict_match("Несъществуващ Отбор", "Лудогорец Разград")
        self.assertIn("Team does not exist", str(ctx.exception))

    def test_different_leagues(self):
        from services.clubs_service import add_club
        from services.leagues_service import create_league, add_club_to_league
        add_club("Отбор А")
        add_club("Отбор Б")

        create_league("Лига 1", "2025")
        lid1 = leagues_repo.resolve_id("Лига 1")
        add_club_to_league(lid1, "Отбор А")

        create_league("Лига 2", "2025")
        lid2 = leagues_repo.resolve_id("Лига 2")
        add_club_to_league(lid2, "Отбор Б")

        with self.assertRaises(ValueError) as ctx:
            ai_service.predict_match("Отбор А", "Отбор Б")
        self.assertIn("Teams are from different leagues", str(ctx.exception))

    def test_less_than_5_matches(self):
        from services.clubs_service import add_club
        add_club("Нов Отбор")
        add_club("Нов Отбор 2")

        from services.leagues_service import create_league, add_club_to_league
        create_league("Нова Лига", "2025")
        lid = leagues_repo.resolve_id("Нова Лига")
        add_club_to_league(lid, "Нов Отбор")
        add_club_to_league(lid, "Нов Отбор 2")

        record_match("Нов Отбор", "Нов Отбор 2", "2025-10-01",
                     home_goals=1, away_goals=0, league_id=lid)

        with self.assertRaises(ValueError) as ctx:
            ai_service.predict_match("Нов Отбор", "Нов Отбор 2")
        self.assertIn("Not enough matches played", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
