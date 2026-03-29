#!/usr/bin/env python3
"""Unit tests for players service (players_service)"""

import os
import sys
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# Ensure tests directory is on path so test helpers (test_config) can be imported
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from src.db import execute_query
from src.services.players_service import add_player, get_players_by_club, update_player_position, update_player_number, update_player_status, delete_player


class TestPlayersService(unittest.TestCase):
    def setUp(self):
        # Prepare test DB and create clubs
        test_config.setup_test_environment()
        from test_config import create_test_clubs
        create_test_clubs()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def test_add_player_success(self):
        clubs = execute_query("SELECT id FROM clubs WHERE name = ?", ("Левски София",), fetch=True)
        club_id = clubs[0]['id']

        res = add_player(club_id, "Тест Играч", "1995-05-05", "България", "FW", 9, "Активен")
        self.assertIn("успешно", res.lower())

        rows = execute_query("SELECT * FROM players WHERE full_name = ?", ("Тест Играч",), fetch=True)
        self.assertIsNotNone(rows)
        self.assertEqual(rows[0]['full_name'], "Тест Играч")

    def test_add_player_missing_fields(self):
        clubs = execute_query("SELECT id FROM clubs WHERE name = ?", ("Левски София",), fetch=True)
        club_id = clubs[0]['id']

        # Missing birth_date
        res = add_player(club_id, "Играч Без Дата", "", "България", "FW", 10, "Активен")
        self.assertIn("невaлидн", res.lower() or res.lower())

    def test_duplicate_player(self):
        clubs = execute_query("SELECT id FROM clubs WHERE name = ?", ("Левски София",), fetch=True)
        club_id = clubs[0]['id']

        add_player(club_id, "Дублиращ Играч", "1994-04-04", "България", "MF", 8, "Активен")
        res = add_player(club_id, "Дублиращ Играч", "1994-04-04", "България", "MF", 8, "Активен")
        self.assertIn("вече съществува", res.lower())

    def test_get_players_by_club(self):
        from test_config import create_test_players
        created = create_test_players()
        self.assertTrue(len(created) > 0)

        res = get_players_by_club("Левски София")
        self.assertIn("Иван Иванов", res)

    def test_update_player_position_and_number_and_status(self):
        clubs = execute_query("SELECT id FROM clubs WHERE name = ?", ("Левски София",), fetch=True)
        club_id = clubs[0]['id']

        add_player(club_id, "Променящ Играч", "1993-03-03", "България", "FW", 11, "Активен")
        # find id
        row = execute_query("SELECT id FROM players WHERE full_name = ?", ("Променящ Играч",), fetch=True)
        pid = row[0]['id']

        res1 = update_player_position(str(pid), "MF")
        self.assertIn("обновена", res1.lower())

        res2 = update_player_number(str(pid), 22)
        self.assertIn("сменен", res2.lower())

        res3 = update_player_status(str(pid), "Травмиран")
        self.assertIn("обновен", res3.lower())

    def test_delete_player(self):
        clubs = execute_query("SELECT id FROM clubs WHERE name = ?", ("Левски София",), fetch=True)
        club_id = clubs[0]['id']

        add_player(club_id, "Играч за изтриване", "1992-02-02", "България", "DF", 5, "Активен")
        row = execute_query("SELECT id FROM players WHERE full_name = ?", ("Играч за изтриване",), fetch=True)
        pid = row[0]['id']

        res = delete_player(str(pid))
        self.assertIn("изтрит", res.lower())


if __name__ == '__main__':
    unittest.main()
