#!/usr/bin/env python3
"""Unit tests for statistics service"""

import os
import sys
import unittest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from src.services.statistics_service import get_club_statistics, get_player_statistics
from src.db import execute_query


class TestStatisticsService(unittest.TestCase):
    def setUp(self):
        test_config.setup_test_environment()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def test_get_club_statistics_by_name(self):
        stats = get_club_statistics('Левски София')
        self.assertIsNotNone(stats)
        self.assertIn('played', stats)
        # Based on sample matches, Levski had 2 matches in sample data
        self.assertEqual(stats['played'], 2)

    def test_get_player_statistics_by_name(self):
        stats = get_player_statistics('Иван Иванов')
        self.assertIsNotNone(stats)
        # Sample data included one goal event for Иван Иванов
        self.assertGreaterEqual(stats['goals'], 1)


if __name__ == '__main__':
    unittest.main()
