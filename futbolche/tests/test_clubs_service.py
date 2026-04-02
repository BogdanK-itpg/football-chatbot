#!/usr/bin/env python3
"""
Unit tests for clubs service (clubs_service.py)
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# Ensure tests directory is on path so test helpers (test_config) can be imported
sys.path.insert(0, os.path.dirname(__file__))

from services.clubs_service import create_club, list_clubs, delete_club
from db import execute_query


class TestClubsService(unittest.TestCase):
    """Test cases for clubs service operations"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_config = __import__('test_config').test_config
        self.test_config.setup_test_environment()
        # Ensure a clean clubs table for this test case so we control inserts
        from db import execute_query
        execute_query("DELETE FROM clubs", fetch=False)
        
        # Create test clubs
        self.test_clubs = [
            "Левски София",
            "ЦСКА София", 
            "Ботев Пловдив",
            "Лудогорец Разград",
            "Черно море Варна"
        ]
        
        for club in self.test_clubs:
            create_club(club)
    
    def tearDown(self):
        """Cleanup test environment"""
        self.test_config.cleanup_test_environment()
    
    def test_add_club_success(self):
        """Test successful club addition"""
        result = create_club("Спартак Варна")
        self.assertIn("успешно", result.lower(), "Should return success message")
        
        # Verify club was added to database
        club = execute_query("SELECT * FROM clubs WHERE name = ?", ("Спартак Варна",), fetch=True)
        self.assertIsNotNone(club, "Club should exist in database")
        self.assertEqual(club[0]['name'], "Спартак Варна")
        self.assertEqual(club[0]['city'], "Unknown")
        self.assertEqual(club[0]['founded_year'], 1900)
    
    def test_add_club_empty_name(self):
        """Test adding club with empty name"""
        result = create_club("")
        self.assertIn("не може да бъде празно", result.lower(), "Should return empty name error")
        
        # Verify club was not added
        club = execute_query("SELECT * FROM clubs WHERE name = ?", ("",), fetch=True)
        self.assertIsNone(club, "Empty name club should not exist")
    
    def test_add_club_whitespace_name(self):
        """Test adding club with whitespace-only name"""
        result = create_club("   ")
        self.assertIn("не може да бъде празно", result.lower(), "Should return empty name error")
        
        # Verify club was not added
        club = execute_query("SELECT * FROM clubs WHERE name = ?", ("   ",), fetch=True)
        self.assertIsNone(club, "Whitespace name club should not exist")
    
    def test_add_club_duplicate_name(self):
        """Test adding club with duplicate name"""
        # Add a club first
        create_club("Дублиращ Клуб")
        
        # Try to add the same club again
        result = create_club("Дублиращ Клуб")
        self.assertIn("вече съществува", result.lower(), "Should return duplicate error")
        
        # Verify only one club exists
        clubs = execute_query("SELECT * FROM clubs WHERE name = ?", ("Дублиращ Клуб",), fetch=True)
        self.assertEqual(len(clubs), 1, "Should have only one club with this name")
    
    def test_add_club_case_insensitive_duplicate(self):
        """Test adding club with case-insensitive duplicate"""
        # Add a club
        create_club("Test Club")
        
        # Try to add with different case
        result = create_club("test club")
        self.assertIn("вече съществува", result.lower(), "Should return duplicate error for case-insensitive match")
    
    def test_get_all_clubs_multiple_clubs(self):
        """Test getting all clubs when multiple clubs exist"""
        result = list_clubs()
        
        # Should be a string with club listings
        self.assertIsInstance(result, str, "Should return a string")
        self.assertIn("Левски София", result, "Should include Levski Sofia")
        self.assertIn("ЦСКА София", result, "Should include CSKA Sofia")
        self.assertIn("Ботев Пловдив", result, "Should include Botev Plovdiv")
        
        # Should have numbered format
        lines = result.split('\n')
        self.assertGreater(len(lines), 1, "Should have multiple clubs")
        
        # Check that lines start with numbers
        for line in lines:
            if line.strip():  # Skip empty lines
                self.assertRegex(line, r'^\d+\.', "Lines should start with number and dot")
    
    def test_get_all_clubs_single_club(self):
        """Test getting all clubs when only one club exists"""
        # Clear all clubs except one
        execute_query("DELETE FROM clubs WHERE name != ?", ("Левски София",), fetch=False)
        
        result = list_clubs()
        self.assertIn("Левски София", result, "Should include the single club")
        self.assertIn("1.", result, "Should have numbered format")
    
    def test_get_all_clubs_no_clubs(self):
        """Test getting all clubs when no clubs exist"""
        # Clear all clubs
        execute_query("DELETE FROM clubs", fetch=False)
        
        result = list_clubs()
        self.assertEqual(result, "Няма добавени клубове.", "Should return no clubs message")
    
    def test_delete_club_success(self):
        """Test successful club deletion"""
        # Add a club to delete
        create_club("Клуб за изтриване")
        
        # Delete the club
        result = delete_club("Клуб за изтриване")
        self.assertIn("изтрит", result.lower(), "Should return deletion success message")
        
        # Verify club was deleted
        club = execute_query("SELECT * FROM clubs WHERE name = ?", ("Клуб за изтриване",), fetch=True)
        self.assertIsNone(club, "Club should be deleted from database")
    
    def test_delete_club_nonexistent(self):
        """Test deleting non-existent club"""
        result = delete_club("Несъществуващ Клуб")
        self.assertIn("няма такъв клуб", result.lower(), "Should return not found error")
        
        # Verify no clubs were deleted
        clubs = execute_query("SELECT COUNT(*) as count FROM clubs", fetch=True)
        self.assertGreater(clubs[0]['count'], 0, "Should not delete existing clubs")
    
    def test_delete_club_case_insensitive(self):
        """Test deleting club with case-insensitive match"""
        # Add a club
        create_club("Test Club")
        
        # Delete with different case
        result = delete_club("test club")
        self.assertIn("изтрит", result.lower(), "Should delete club with case-insensitive match")
        
        # Verify club was deleted
        club = execute_query("SELECT * FROM clubs WHERE name = ?", ("Test Club",), fetch=True)
        self.assertIsNone(club, "Club should be deleted")
    
    def test_delete_club_cascade_delete_players(self):
        """Test that deleting a club cascades to delete players"""
        # Add a club and a player
        create_club("Клуб с играчи")
        club = execute_query("SELECT id FROM clubs WHERE name = ?", ("Клуб с играчи",), fetch=True)
        club_id = club[0]['id']
        
        # Add a player to the club
        from services.players_service import add_player
        add_player(club_id, "Тестов Играч", "1990-01-01", "България", "GK", 1, "Активен")
        
        # Verify player exists
        players = execute_query("SELECT COUNT(*) as count FROM players WHERE club_id = ?", (club_id,), fetch=True)
        initial_player_count = players[0]['count']
        self.assertGreater(initial_player_count, 0, "Should have players before deletion")
        
        # Delete the club
        delete_club("Клуб с играчи")
        
        # Verify players were also deleted (cascade delete)
        players = execute_query("SELECT COUNT(*) as count FROM players WHERE club_id = ?", (club_id,), fetch=True)
        final_player_count = players[0]['count']
        self.assertEqual(final_player_count, 0, "Players should be cascade deleted")
    
    def test_add_club_with_special_characters(self):
        """Test adding club with special characters in name"""
        club_name = "Клуб с спец. символи!@#"
        result = create_club(club_name)
        self.assertIn("успешно", result.lower(), "Should add club with special characters")
        
        # Verify club was added
        club = execute_query("SELECT * FROM clubs WHERE name = ?", (club_name,), fetch=True)
        self.assertIsNotNone(club, "Club with special characters should exist")
    
    def test_add_club_with_long_name(self):
        """Test adding club with very long name"""
        long_name = "A" * 200  # Very long club name
        result = create_club(long_name)
        self.assertIn("успешно", result.lower(), "Should add club with long name")
        
        # Verify club was added
        club = execute_query("SELECT * FROM clubs WHERE name = ?", (long_name,), fetch=True)
        self.assertIsNotNone(club, "Long name club should exist")
    
    def test_get_all_clubs_ordering(self):
        """Test that clubs are returned in correct order"""
        result = list_clubs()
        lines = result.split('\n')
        
        # Extract club names and their order
        club_order = []
        for line in lines:
            if line.strip():
                # Extract club name after the number and dot
                parts = line.split('. ', 1)
                if len(parts) > 1:
                    club_order.append(parts[1])
        
        # Check that order is consistent (should be by ID)
        expected_order = ["Левски София", "ЦСКА София", "Ботев Пловдив", "Лудогорец Разград", "Черно море Варна"]
        self.assertEqual(club_order, expected_order, "Clubs should be ordered by ID")
    
    @patch('services.clubs_service.execute')
    def test_add_club_database_error(self, mock_execute):
        """Test handling of database errors during club addition"""
        # Mock execute to raise an exception
        mock_execute.side_effect = Exception("Database error")
        
        result = create_club("Test Club")
        self.assertIn("Грешка", result, "Should handle database error gracefully")
    
    @patch('services.clubs_service.fetch_all')
    def test_get_all_clubs_database_error(self, mock_fetch_all):
        """Test handling of database errors during club listing"""
        # Mock fetch_all to raise an exception
        mock_fetch_all.side_effect = Exception("Database error")
        
        result = list_clubs()
        self.assertEqual(result, "Няма добавени клубове.", "Should handle database error gracefully")
    
    @patch('services.clubs_service.execute')
    def test_delete_club_database_error(self, mock_execute):
        """Test handling of database errors during club deletion"""
        # Ensure the club exists so deletion will attempt to execute (insert directly)
        from db import execute_query
        execute_query("INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)", ("Test Club", "Unknown", 1900), fetch=False)
        # Mock execute to raise an exception
        mock_execute.side_effect = Exception("Database error")

        result = delete_club("Test Club")
        self.assertIn("Грешка", result, "Should handle database error gracefully")


if __name__ == '__main__':
    unittest.main()