#!/usr/bin/env python3
"""Unit tests for advanced player metrics (goals/90, assists/90, minutes)"""

import os
import sys
import unittest

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_config import test_config
from services.statistics_service import get_player_advanced_metrics, get_player_statistics

class TestPlayerMetrics(unittest.TestCase):
    def setUp(self):
        test_config.setup_test_environment()

    def tearDown(self):
        test_config.cleanup_test_environment()

    def test_metrics_for_player_with_goal_and_appearance(self):
        # Ivan Ivanov in sample data has one goal and one appearance
        stats = get_player_statistics('Иван Иванов')
        self.assertIsNotNone(stats)
        adv = get_player_advanced_metrics('Иван Иванов')
        self.assertIsNotNone(adv)
        # minutes should be appearances * 90 -> at least 90
        self.assertGreaterEqual(adv['minutes_played'], 90)
        # goals_per_90 should be numeric and >= 0
        self.assertIsInstance(adv['goals_per_90'], float)
        self.assertGreaterEqual(adv['goals_per_90'], 0.0)

if __name__ == '__main__':
    unittest.main()
