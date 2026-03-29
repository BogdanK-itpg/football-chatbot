#!/usr/bin/env python3
"""
Unit tests for database operations (db.py)
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Ensure tests directory is on path so test helpers (test_config) can be imported
sys.path.insert(0, os.path.dirname(__file__))

import src.db
from src.db import initialize_database, get_connection, execute_query


class TestDatabaseOperations(unittest.TestCase):
    """Test cases for database operations"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_config = __import__('test_config').test_config
        self.test_config.setup_test_environment()
        
    def tearDown(self):
        """Cleanup test environment"""
        self.test_config.cleanup_test_environment()
    
    def test_initialize_database_creates_new_database(self):
        """Test that initialize_database creates a new database file"""
        # Ensure database doesn't exist
        if os.path.exists(src.db.DB_PATH):
            os.remove(src.db.DB_PATH)
        
        # Initialize database
        initialize_database()
        
        # Check that database file was created
        self.assertTrue(os.path.exists(db.DB_PATH), "Database file should be created")
        
        # Check that tables exist
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clubs'")
        self.assertIsNotNone(cursor.fetchone(), "Clubs table should exist")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
        self.assertIsNotNone(cursor.fetchone(), "Players table should exist")
        conn.close()
    
    def test_initialize_database_populates_sample_data(self):
        """Test that initialize_database populates sample data"""
        # Get club count
        clubs = execute_query("SELECT COUNT(*) as count FROM clubs", fetch=True)
        self.assertEqual(clubs[0]['count'], 8, "Should have 8 sample clubs")
        
        # Get player count
        players = execute_query("SELECT COUNT(*) as count FROM players", fetch=True)
        self.assertEqual(players[0]['count'], 38, "Should have 38 sample players")
        
        # Check specific clubs
        levski = execute_query("SELECT * FROM clubs WHERE name = 'Левски София'", fetch=True)
        self.assertIsNotNone(levski, "Levski Sofia club should exist")
        self.assertEqual(levski[0]['city'], 'София')
        self.assertEqual(levski[0]['founded_year'], 1914)
    
    def test_get_connection_returns_valid_connection(self):
        """Test that get_connection returns a valid database connection"""
        conn = get_connection()
        self.assertIsNotNone(conn, "Connection should not be None")
        
        # Test that connection works
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        
        conn.close()
    
    def test_get_connection_handles_database_error(self):
        """Test that get_connection handles database errors gracefully"""
        # Mock sqlite3.connect to raise an error
        with patch('sqlite3.connect', side_effect=Exception("Database error")):
            conn = get_connection()
            self.assertIsNone(conn, "Should return None on database error")
    
    def test_execute_query_fetch_true(self):
        """Test execute_query with fetch=True"""
        result = execute_query("SELECT COUNT(*) as count FROM clubs", fetch=True)
        self.assertIsNotNone(result, "Should return results")
        self.assertEqual(len(result), 1, "Should return one row")
        self.assertEqual(result[0]['count'], 8, "Should have 8 clubs")
    
    def test_execute_query_fetch_false(self):
        """Test execute_query with fetch=False"""
        result = execute_query("INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)", 
                              ("Test Club", "Test City", 2000), fetch=False)
        self.assertTrue(result, "Should return True for successful insert")
        
        # Verify insertion
        test_club = execute_query("SELECT * FROM clubs WHERE name = 'Test Club'", fetch=True)
        self.assertIsNotNone(test_club, "Inserted club should exist")
        self.assertEqual(test_club[0]['name'], "Test Club")
        self.assertEqual(test_club[0]['city'], "Test City")
        self.assertEqual(test_club[0]['founded_year'], 2000)
    
    def test_execute_query_with_parameters(self):
        """Test execute_query with parameters"""
        # Insert with parameters
        result = execute_query(
            "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
            ("CSKA Sofia", "София", 1948), fetch=False
        )
        self.assertTrue(result, "Insert should succeed")
        
        # Query with parameters
        cska = execute_query(
            "SELECT * FROM clubs WHERE name = ? AND city = ?",
            ("CSKA Sofia", "София"), fetch=True
        )
        self.assertIsNotNone(cska, "CSKA Sofia should exist")
        self.assertEqual(cska[0]['name'], "CSKA Sofia")
    
    def test_execute_query_handles_error(self):
        """Test execute_query handles database errors"""
        # Try invalid SQL
        result = execute_query("INVALID SQL STATEMENT", fetch=True)
        self.assertIsNone(result, "Should return None on SQL error")
    
    def test_database_foreign_key_constraints(self):
        """Test that foreign key constraints work"""
        # Try to insert player with non-existent club
        result = execute_query(
            "INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (999, "Test Player", "1990-01-01", "Test", "GK", 1, "Active"), fetch=False
        )
        # Should fail due to foreign key constraint
        self.assertIsNone(result, "Should fail due to foreign key constraint")
    
    def test_database_unique_constraints(self):
        """Test that unique constraints work"""
        # Try to insert duplicate club name
        result = execute_query(
            "INSERT INTO clubs (name, city, founded_year) VALUES (?, ?, ?)",
            ("Левски София", "Test City", 2000), fetch=False
        )
        # Should fail due to unique constraint
        self.assertIsNone(result, "Should fail due to unique constraint")
    
    def test_database_cascade_delete(self):
        """Test that cascade delete works for foreign keys"""
        # Get initial player count
        initial_players = execute_query("SELECT COUNT(*) as count FROM players", fetch=True)
        initial_count = initial_players[0]['count']
        
        # Delete a club
        execute_query("DELETE FROM clubs WHERE name = ?", ("Левски София",), fetch=False)
        
        # Check that players were also deleted
        final_players = execute_query("SELECT COUNT(*) as count FROM players", fetch=True)
        final_count = final_players[0]['count']
        
        # Should have fewer players due to cascade delete
        self.assertLess(final_count, initial_count, "Player count should decrease after club deletion")
    
    def test_database_schema_validation(self):
        """Test that database schema is correct"""
        # Check clubs table schema
        columns = execute_query("PRAGMA table_info(clubs)", fetch=True)
        column_names = [col['name'] for col in columns]
        expected_columns = ['id', 'name', 'city', 'founded_year']
        
        for col in expected_columns:
            self.assertIn(col, column_names, f"Column {col} should exist in clubs table")
        
        # Check players table schema
        columns = execute_query("PRAGMA table_info(players)", fetch=True)
        column_names = [col['name'] for col in columns]
        expected_columns = ['id', 'club_id', 'full_name', 'birth_date', 'nationality', 'position', 'number', 'status']
        
        for col in expected_columns:
            self.assertIn(col, column_names, f"Column {col} should exist in players table")
        
        # Check foreign key constraint
        fk_info = execute_query("PRAGMA foreign_key_list(players)", fetch=True)
        self.assertGreater(len(fk_info), 0, "Players table should have foreign key constraints")
        self.assertEqual(fk_info[0]['table'], 'clubs', "Should reference clubs table")


if __name__ == '__main__':
    unittest.main()