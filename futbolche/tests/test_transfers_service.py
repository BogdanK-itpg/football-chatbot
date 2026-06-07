#!/usr/bin/env python3
"""Tests for transfers service (transfers_service)"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config, create_test_clubs, create_test_players
from db import execute_query, fetch_one
from services.transfers_service import transfer_player, list_transfers_by_player, list_transfers_by_club
from repositories import transfers_repo


class TestTransfersService(unittest.TestCase):
    def setUp(self):
        test_config.setup_test_environment()
        create_test_clubs()
        create_test_players()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def _get_player_and_target(self):
        player = execute_query("SELECT id, club_id FROM players WHERE club_id IS NOT NULL LIMIT 1", fetch=True)[0]
        pid = player['id']
        current_cid = player['club_id']
        club = execute_query("SELECT id FROM clubs WHERE id != ? LIMIT 1", (current_cid,), fetch=True)[0]
        target_cid = club['id']
        target_name = execute_query("SELECT name FROM clubs WHERE id = ?", (target_cid,), fetch=True)[0]['name']
        return pid, current_cid, target_cid, target_name

    def test_transfer_success(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        res = transfer_player(str(pid), target_name, from_club_identifier=str(current_cid), transfer_date='2026-06-01')
        self.assertIn('трансфериран', res.lower())
        row = execute_query("SELECT club_id FROM players WHERE id = ?", (pid,), fetch=True)
        self.assertEqual(row[0]['club_id'], target_cid)
        transfer_rows = execute_query(
            "SELECT * FROM transfers WHERE player_id = ? AND to_club_id = ?",
            (pid, target_cid), fetch=True
        )
        self.assertIsNotNone(transfer_rows)
        self.assertGreaterEqual(len(transfer_rows), 1)

    def test_transfer_creates_transfer_record(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        transfer_player(str(pid), target_name, from_club_identifier=str(current_cid), transfer_date='2026-06-15', fee='100000')
        row = fetch_one("SELECT * FROM transfers WHERE player_id = ? AND to_club_id = ?", (pid, target_cid))
        self.assertIsNotNone(row)
        self.assertEqual(row['from_club_id'], current_cid)
        self.assertEqual(row['to_club_id'], target_cid)
        self.assertEqual(row['transfer_date'], '2026-06-15')
        self.assertEqual(row['fee'], 100000.0)

    def test_transfer_wrong_current_club(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        wrong_club = execute_query(
            "SELECT id FROM clubs WHERE id != ? AND id != ? LIMIT 1",
            (current_cid, target_cid), fetch=True
        )[0]
        original_club = execute_query("SELECT club_id FROM players WHERE id = ?", (pid,), fetch=True)[0]['club_id']
        count_before = execute_query(
            "SELECT COUNT(*) as cnt FROM transfers WHERE player_id = ?", (pid,), fetch=True
        )[0]['cnt']
        res = transfer_player(str(pid), target_name, from_club_identifier=str(wrong_club['id']))
        self.assertIn("не играе", res.lower())
        final_club = execute_query("SELECT club_id FROM players WHERE id = ?", (pid,), fetch=True)[0]['club_id']
        self.assertEqual(final_club, original_club)
        count_after = execute_query(
            "SELECT COUNT(*) as cnt FROM transfers WHERE player_id = ?", (pid,), fetch=True
        )[0]['cnt']
        self.assertEqual(count_after, count_before)

    def test_transfer_to_same_club_rejected(self):
        player = execute_query("SELECT id, club_id FROM players LIMIT 1", fetch=True)[0]
        pid = player['id']
        cid = player['club_id']
        club_name = execute_query("SELECT name FROM clubs WHERE id = ?", (cid,), fetch=True)[0]['name']
        count_before = execute_query("SELECT COUNT(*) as cnt FROM transfers", fetch=True)[0]['cnt']
        res = transfer_player(str(pid), club_name, from_club_identifier=str(cid))
        self.assertIn("вече е в този клуб", res.lower())
        count_after = execute_query("SELECT COUNT(*) as cnt FROM transfers", fetch=True)[0]['cnt']
        self.assertEqual(count_after, count_before)

    def test_transfer_invalid_player(self):
        res = transfer_player('99999', 'Левски София')
        self.assertIn("не съществува", res.lower())

    def test_transfer_invalid_club(self):
        player = execute_query("SELECT id FROM players LIMIT 1", fetch=True)[0]
        pid = player['id']
        res = transfer_player(str(pid), 'Несъществуващ Клуб', from_club_identifier='1')
        self.assertIn("не съществува", res.lower())

    def test_transfer_invalid_date(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        res = transfer_player(str(pid), target_name, from_club_identifier=str(current_cid), transfer_date='invalid-date')
        self.assertIn("формат", res.lower())

    def test_transfer_negative_fee(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        res = transfer_player(str(pid), target_name, from_club_identifier=str(current_cid), fee='-100')
        self.assertIn("отрицателн", res.lower())

    def test_transfer_free_agent_to_club(self):
        player = execute_query("SELECT id, club_id FROM players LIMIT 1", fetch=True)[0]
        pid = player['id']
        target = execute_query("SELECT id, name FROM clubs WHERE id != ? LIMIT 1", (player['club_id'],), fetch=True)[0]
        execute_query("UPDATE players SET club_id = NULL WHERE id = ?", (pid,), fetch=False)
        res = transfer_player(str(pid), target['name'], from_club_identifier='няма')
        self.assertIn('трансфериран', res.lower())
        row = execute_query("SELECT club_id FROM players WHERE id = ?", (pid,), fetch=True)
        self.assertEqual(row[0]['club_id'], target['id'])

    def test_list_transfers_by_player(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        transfer_player(str(pid), target_name, from_club_identifier=str(current_cid), transfer_date='2026-07-01')
        res = list_transfers_by_player(str(pid))
        self.assertIn('трансфери', res.lower())
        self.assertIn(target_name, res)

    def test_list_transfers_by_player_not_found(self):
        res = list_transfers_by_player('99999')
        self.assertIn("не съществува", res.lower())

    def test_list_transfers_by_club(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        player_name = execute_query("SELECT full_name FROM players WHERE id = ?", (pid,), fetch=True)[0]['full_name']
        transfer_player(str(pid), target_name, from_club_identifier=str(current_cid), transfer_date='2026-08-01')
        res = list_transfers_by_club(str(target_cid))
        self.assertIn('трансфери', res.lower())
        self.assertIn(player_name, res)

    def test_list_transfers_by_club_not_found(self):
        res = list_transfers_by_club('99999')
        self.assertIn("не съществува", res.lower())

    def test_transfer_nonexistent_from_club(self):
        pid, current_cid, target_cid, target_name = self._get_player_and_target()
        res = transfer_player(str(pid), target_name, from_club_identifier='Несъществуващ Клуб')
        self.assertIn("не съществува", res.lower())

    def test_transfer_player_not_in_from_club_free_agent_mismatch(self):
        execute_query("UPDATE players SET club_id = NULL WHERE id = 1", fetch=False)
        target = execute_query("SELECT id, name FROM clubs LIMIT 1", fetch=True)[0]
        res = transfer_player('1', target['name'], from_club_identifier='Левски София')
        self.assertIn("свободен агент", res.lower())


if __name__ == '__main__':
    unittest.main()
