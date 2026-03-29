#!/usr/bin/env python3
"""
Test configuration and utilities for football chatbot tests.
"""



# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestConfig:
    """Test configuration class"""
    
    def __init__(self):
        self.test_db_path = None
        self.original_db_path = None
        self.original_schema_path = None
        
    def setup_test_environment(self):
        """Setup test environment with temporary database"""
        # Store original paths
        import src.db as real_db

        # Store original paths
        self.original_db_path = real_db.DB_PATH
        self.original_schema_path = real_db.SCHEMA_PATH

        # Create temporary directory and test DB path
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, 'test_football.db')

        # Override db paths on the real module for testing
        real_db.DB_PATH = self.test_db_path
        real_db.SCHEMA_PATH = self.original_schema_path

        # Reinitialize database with test path
        real_db.initialize_database()

        return self.test_db_path
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        try:
            import src.db as real_db
            # restore original paths
            if self.original_db_path is not None:
                real_db.DB_PATH = self.original_db_path
            if self.original_schema_path is not None:
                real_db.SCHEMA_PATH = self.original_schema_path
        except Exception:
            pass
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

# Global test configuration instance
test_config = TestConfig()

def setup_function():
    """Setup function for pytest"""
    test_config.setup_test_environment()

def teardown_function():
    """Teardown function for pytest"""
    test_config.cleanup_test_environment()

def create_test_clubs():
    """Create test clubs for testing"""
    from src.services.clubs_service import create_club
    clubs = [
        "Левски София",
        "ЦСКА София", 
        "Ботев Пловдив",
        "Лудогорец Разград",
        "Черно море Варна"
    ]
    
    created_clubs = []
    for club in clubs:
        result = create_club(club)
        if result and "успешно" in result.lower():
            created_clubs.append(club)
    
    return created_clubs

def create_test_players():
    """Create test players for testing"""
    from src.services.players_service import add_player
    from src.db import execute_query
    
    # Get club IDs
    clubs = execute_query("SELECT id, name FROM clubs", fetch=True)
    club_map = {club['name']: club['id'] for club in clubs}
    
    players = [
        # Levski Sofia players
        (club_map["Левски София"], "Иван Иванов", "1995-03-15", "България", "GK", 1, "Активен"),
        (club_map["Левски София"], "Петър Петров", "1998-07-22", "България", "DF", 4, "Активен"),
        (club_map["Левски София"], "Мария Георгиева", "1997-11-08", "България", "MF", 10, "Активен"),
        
        # CSKA Sofia players
        (club_map["ЦСКА София"], "Георги Димитров", "1994-05-12", "България", "GK", 1, "Активен"),
        (club_map["ЦСКА София"], "Димитър Иванов", "1997-12-25", "България", "MF", 8, "Активен"),
        
        # Botev Plovdiv players
        (club_map["Ботев Пловдив"], "Мартин Камиларов", "1996-02-14", "България", "GK", 1, "Активен"),
        (club_map["Ботев Пловдив"], "Илия Илиев", "1995-08-20", "България", "DF", 5, "Активен"),
    ]
    
    created_players = []
    for player_data in players:
        result = add_player(*player_data)
        # Treat both successful insert and 'already exists' as creation for tests
        if result:
            low = result.lower()
            if "успешно" in low or "вече съществува" in low:
                created_players.append(player_data[1])  # player name
    
    return created_players