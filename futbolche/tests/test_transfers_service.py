#!/usr/bin/env python3
"""Tests for transfers service (transfers_service)"""

import os
import sys
import unittest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# Ensure tests directory is on path so test helpers (test_config) can be imported
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config, create_test_clubs, create_test_players
from db import execute_query
from services.transfers_service import transfer_player


class TestTransfersService(unittest.TestCase):
    def setUp(self):
        test_config.setup_test_environment()
        create_test_clubs()
        create_test_players()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def test_transfer_success(self):
        # pick a player and a different club
        player = execute_query("SELECT id, club_id FROM players LIMIT 1", fetch=True)[0]
        pid = player['id']
        current_cid = player['club_id']

        # pick a club that is different
        club = execute_query("SELECT id FROM clubs WHERE id != ? LIMIT 1", (current_cid,), fetch=True)[0]
        target_cid = club['id']

        res = transfer_player(str(pid), str(target_cid))
        self.assertIn('трансфериран', res.lower())

        # verify DB updated
        row = execute_query("SELECT club_id FROM players WHERE id = ?", (pid,), fetch=True)
        self.assertEqual(row[0]['club_id'], target_cid)

    def test_transfer_invalid_player(self):
        res = transfer_player('99999', 'Левски София')
        self.assertIn("не съществува", res.lower())

    def test_transfer_invalid_club(self):
        # use an existing player
        player = execute_query("SELECT id FROM players LIMIT 1", fetch=True)[0]
        pid = player['id']
        res = transfer_player(str(pid), 'Несъществуващ Клуб')
        self.assertIn("не съществува", res.lower())


if __name__ == '__main__':
    unittest.main()
