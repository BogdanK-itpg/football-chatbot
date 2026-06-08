#!/usr/bin/env python3
"""Tests for the Standings module — repository, service, and handler."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from services.standings_service import calculate_standings
from services.leagues_service import create_league, add_club_to_league
from services.matches_service import record_match
from repositories import leagues_repo, matches_repo
from handlers.handler_standings import handle_show_standings
from db import execute, fetch_one, fetch_all


class TestStandingsService(unittest.TestCase):

    def setUp(self):
        test_config.setup_test_environment()
        self._create_data()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def _create_data(self):
        from services.clubs_service import add_club
        add_club("Левски София")
        add_club("ЦСКА София")
        add_club("Ботев Пловдив")
        add_club("Лудогорец Разград")

    def _create_league(self, name="Първа Лига", season="2025/2026", teams=None):
        create_league(name, season)
        lid = leagues_repo.resolve_id(name)
        if teams is None:
            teams = ["Левски София", "ЦСКА София", "Ботев Пловдив", "Лудогорец Разград"]
        for t in teams:
            add_club_to_league(lid, t)
        return lid

    # ---- Scenario 1: No played matches ----
    def test_standings_no_played_matches(self):
        lid = self._create_league()
        table = calculate_standings("Първа Лига", "2025/2026")
        self.assertEqual(len(table), 4)
        for row in table:
            self.assertEqual(row['mp'], 0)
            self.assertEqual(row['w'], 0)
            self.assertEqual(row['d'], 0)
            self.assertEqual(row['l'], 0)
            self.assertEqual(row['gf'], 0)
            self.assertEqual(row['ga'], 0)
            self.assertEqual(row['gd'], 0)
            self.assertEqual(row['pts'], 0)

    # ---- Scenario 2: One match ----
    def test_standings_one_match(self):
        lid = self._create_league()
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=2, away_goals=1, league_id=lid)
        table = calculate_standings("Първа Лига", "2025/2026")
        self.assertEqual(len(table), 4)

        levski = next(r for r in table if r['team'] == "Левски София")
        cska = next(r for r in table if r['team'] == "ЦСКА София")

        self.assertEqual(levski['pts'], 3)
        self.assertEqual(levski['mp'], 1)
        self.assertEqual(levski['w'], 1)
        self.assertEqual(levski['gf'], 2)
        self.assertEqual(levski['ga'], 1)
        self.assertEqual(levski['gd'], 1)

        self.assertEqual(cska['pts'], 0)
        self.assertEqual(cska['mp'], 1)
        self.assertEqual(cska['l'], 1)
        self.assertEqual(cska['gf'], 1)
        self.assertEqual(cska['ga'], 2)
        self.assertEqual(cska['gd'], -1)

    # ---- Scenario 3: Multiple matches ----
    def test_standings_multiple_matches(self):
        lid = self._create_league()
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=2, away_goals=0, league_id=lid)
        record_match("Ботев Пловдив", "Лудогорец Разград", "2025-08-02",
                     home_goals=1, away_goals=1, league_id=lid)
        record_match("Левски София", "Ботев Пловдив", "2025-08-08",
                     home_goals=3, away_goals=1, league_id=lid)
        record_match("ЦСКА София", "Лудогорец Разград", "2025-08-09",
                     home_goals=0, away_goals=2, league_id=lid)

        table = calculate_standings("Първа Лига", "2025/2026")
        self.assertEqual(len(table), 4)

        levski = next(r for r in table if r['team'] == "Левски София")
        self.assertEqual(levski['pts'], 6)
        self.assertEqual(levski['mp'], 2)
        self.assertEqual(levski['w'], 2)
        self.assertEqual(levski['gf'], 5)
        self.assertEqual(levski['ga'], 1)

        ludogorets = next(r for r in table if r['team'] == "Лудогорец Разград")
        self.assertEqual(ludogorets['pts'], 4)
        self.assertEqual(ludogorets['mp'], 2)
        self.assertEqual(ludogorets['w'], 1)
        self.assertEqual(ludogorets['d'], 1)
        self.assertEqual(ludogorets['gf'], 3)
        self.assertEqual(ludogorets['ga'], 1)

        botev = next(r for r in table if r['team'] == "Ботев Пловдив")
        self.assertEqual(botev['pts'], 1)

        cska = next(r for r in table if r['team'] == "ЦСКА София")
        self.assertEqual(cska['pts'], 0)

        self.assertEqual(table[0]['team'], "Левски София")
        self.assertEqual(table[1]['team'], "Лудогорец Разград")
        self.assertEqual(table[2]['team'], "Ботев Пловдив")
        self.assertEqual(table[3]['team'], "ЦСКА София")

    # ---- Scenario 4: Tie on points - sorted by GD then GF ----
    def test_standings_tiebreaker(self):
        lid = self._create_league()
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=1, away_goals=0, league_id=lid)
        record_match("Ботев Пловдив", "Лудогорец Разград", "2025-08-01",
                     home_goals=3, away_goals=2, league_id=lid)
        record_match("Левски София", "Ботев Пловдив", "2025-08-08",
                     home_goals=0, away_goals=0, league_id=lid)
        record_match("ЦСКА София", "Лудогорец Разград", "2025-08-08",
                     home_goals=2, away_goals=1, league_id=lid)

        table = calculate_standings("Първа Лига", "2025/2026")
        levski = next(r for r in table if r['team'] == "Левски София")
        botev = next(r for r in table if r['team'] == "Ботев Пловдив")

        self.assertEqual(levski['pts'], 4)
        self.assertEqual(botev['pts'], 4)
        self.assertEqual(levski['gd'], 1)
        self.assertEqual(botev['gd'], 1)
        self.assertEqual(levski['gf'], 1)
        self.assertEqual(botev['gf'], 3)

        botev_pos = next(i for i, r in enumerate(table) if r['team'] == "Ботев Пловдив")
        levski_pos = next(i for i, r in enumerate(table) if r['team'] == "Левски София")
        self.assertLess(botev_pos, levski_pos)

    # ---- Scenario 5: Non-existent league ----
    def test_standings_nonexistent_league(self):
        table = calculate_standings("Несъществуваща Лига", "2025")
        self.assertEqual(table, [])

    # ---- Handler output format ----
    def test_standings_handler_empty(self):
        lid = self._create_league()
        result = handle_show_standings({
            'league_identifier': 'Първа Лига',
            'season': '2025/2026'
        })
        self.assertIn("Няма изиграни мачове", result)
        self.assertIn("Левски София", result)

    def test_standings_handler_with_matches(self):
        lid = self._create_league()
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=2, away_goals=1, league_id=lid)
        result = handle_show_standings({
            'league_identifier': 'Първа Лига',
            'season': '2025/2026'
        })
        self.assertIn("1.", result)
        self.assertIn("Левски София", result)
        self.assertIn("3", result)
        self.assertNotIn("Няма изиграни мачове", result)

    def test_standings_handler_no_league(self):
        result = handle_show_standings({
            'league_identifier': 'Невалидна Лига',
            'season': '2025'
        })
        self.assertIn("Няма намерена лига", result)

    # ---- Only played matches count ----
    def test_standings_unplayed_match_excluded(self):
        lid = self._create_league()
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=2, away_goals=1, league_id=lid)
        record_match("Ботев Пловдив", "Лудогорец Разград", "2025-08-02",
                     league_id=lid)

        table = calculate_standings("Първа Лига", "2025/2026")
        levski = next(r for r in table if r['team'] == "Левски София")
        botev = next(r for r in table if r['team'] == "Ботев Пловдив")
        ludogorets = next(r for r in table if r['team'] == "Лудогорец Разград")

        self.assertEqual(levski['mp'], 1)
        self.assertEqual(botev['mp'], 0)
        self.assertEqual(ludogorets['mp'], 0)

    # ---- NULL score excluded ----
    def test_standings_null_score_excluded(self):
        lid = self._create_league()
        execute(
            "INSERT INTO matches (home_team_id, away_team_id, match_date, league_id, is_played) "
            "VALUES ((SELECT id FROM clubs WHERE name='Левски София'), "
            "(SELECT id FROM clubs WHERE name='ЦСКА София'), '2025-08-01', ?, 1)",
            (lid,)
        )
        record_match("Ботев Пловдив", "Лудогорец Разград", "2025-08-02",
                     home_goals=1, away_goals=0, league_id=lid)

        table = calculate_standings("Първа Лига", "2025/2026")
        levski = next(r for r in table if r['team'] == "Левски София")
        self.assertEqual(levski['mp'], 0)

    # ---- Season filtering ----
    def test_standings_season_filter(self):
        create_league("Първа Лига", "2024/2025")
        lid1 = leagues_repo.get_by_name_season("Първа Лига", "2024/2025")['id']
        for t in ["Левски София", "ЦСКА София"]:
            add_club_to_league(lid1, t)
        record_match("Левски София", "ЦСКА София", "2024-09-01",
                     home_goals=1, away_goals=1, league_id=lid1)

        create_league("Първа Лига", "2025/2026")
        lid2 = leagues_repo.get_by_name_season("Първа Лига", "2025/2026")['id']
        for t in ["Левски София", "ЦСКА София"]:
            add_club_to_league(lid2, t)

        table = calculate_standings("Първа Лига", "2025/2026")
        self.assertEqual(len(table), 2)
        for row in table:
            self.assertEqual(row['mp'], 0)


    # ---- Draw outcome ----
    def test_standings_draw_outcome(self):
        lid = self._create_league()
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=1, away_goals=1, league_id=lid)
        table = calculate_standings("Първа Лига", "2025/2026")

        levski = next(r for r in table if r['team'] == "Левски София")
        cska = next(r for r in table if r['team'] == "ЦСКА София")

        self.assertEqual(levski['pts'], 1)
        self.assertEqual(levski['mp'], 1)
        self.assertEqual(levski['d'], 1)
        self.assertEqual(levski['gf'], 1)
        self.assertEqual(levski['ga'], 1)
        self.assertEqual(levski['gd'], 0)

        self.assertEqual(cska['pts'], 1)
        self.assertEqual(cska['d'], 1)

    # ---- Head-to-head tiebreaker ----
    def test_standings_head_to_head_tiebreaker(self):
        lid = self._create_league()
        # Levski and CSKA end with equal PTS(4), GD(0), GF(1)
        # Head-to-head: Levski beat CSKA 1-0, so Levski should be ahead
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=1, away_goals=0, league_id=lid)
        record_match("Левски София", "Ботев Пловдив", "2025-08-08",
                     home_goals=0, away_goals=0, league_id=lid)
        record_match("Левски София", "Лудогорец Разград", "2025-08-15",
                     home_goals=0, away_goals=1, league_id=lid)
        record_match("ЦСКА София", "Ботев Пловдив", "2025-08-08",
                     home_goals=1, away_goals=0, league_id=lid)
        record_match("ЦСКА София", "Лудогорец Разград", "2025-08-15",
                     home_goals=0, away_goals=0, league_id=lid)

        table = calculate_standings("Първа Лига", "2025/2026")
        levski = next(r for r in table if r['team'] == "Левски София")
        cska = next(r for r in table if r['team'] == "ЦСКА София")

        # Both end with 4pts, GD=0, GF=1
        self.assertEqual(levski['pts'], 4)
        self.assertEqual(cska['pts'], 4)
        self.assertEqual(levski['gd'], 0)
        self.assertEqual(cska['gd'], 0)
        self.assertEqual(levski['gf'], 1)
        self.assertEqual(cska['gf'], 1)

        # Head-to-head: Levski beat CSKA 1-0, so Levski should be ahead
        levski_pos = next(i for i, r in enumerate(table) if r['team'] == "Левски София")
        cska_pos = next(i for i, r in enumerate(table) if r['team'] == "ЦСКА София")
        self.assertLess(levski_pos, cska_pos)

    # ---- Alphabetical tiebreaker when all stats are equal ----
    def test_standings_alphabetical_tiebreaker(self):
        lid = self._create_league()
        # All teams have exactly the same stats: 0-0 draws
        record_match("Левски София", "ЦСКА София", "2025-08-01",
                     home_goals=0, away_goals=0, league_id=lid)
        record_match("Ботев Пловдив", "Лудогорец Разград", "2025-08-08",
                     home_goals=0, away_goals=0, league_id=lid)
        record_match("Левски София", "Ботев Пловдив", "2025-08-15",
                     home_goals=0, away_goals=0, league_id=lid)
        record_match("ЦСКА София", "Лудогорец Разград", "2025-08-15",
                     home_goals=0, away_goals=0, league_id=lid)
        record_match("Левски София", "Лудогорец Разград", "2025-08-22",
                     home_goals=0, away_goals=0, league_id=lid)
        record_match("ЦСКА София", "Ботев Пловдив", "2025-08-22",
                     home_goals=0, away_goals=0, league_id=lid)

        table = calculate_standings("Първа Лига", "2025/2026")
        self.assertEqual(len(table), 4)

        for row in table:
            self.assertEqual(row['pts'], 3)
            self.assertEqual(row['gd'], 0)
            self.assertEqual(row['gf'], 0)

        # All tied — order should be alphabetical: Ботев, Левски, Лудогорец, ЦСКА
        self.assertEqual(table[0]['team'], "Ботев Пловдив")
        self.assertEqual(table[1]['team'], "Левски София")
        self.assertEqual(table[2]['team'], "Лудогорец Разград")
        self.assertEqual(table[3]['team'], "ЦСКА София")


if __name__ == '__main__':
    unittest.main()
