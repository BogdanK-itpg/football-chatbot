#!/usr/bin/env python3
"""
Test setup script for football chatbot.
Creates test data: 3+ clubs and 10+ players with valid data.
"""

import os
import sys
import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db import initialize_database, execute_query
from clubs_service import add_club
from players_service import add_player

def clear_existing_data():
    """Clear existing data from database for clean test setup"""
    execute_query("DELETE FROM players", fetch=False)
    execute_query("DELETE FROM clubs", fetch=False)
    print("[TEST SETUP] Cleared existing data")

def create_test_clubs():
    """Create test clubs"""
    clubs = [
        ("Левски София", "София", 1914),
        ("ЦСКА София", "София", 1948),
        ("Ботев Пловдив", "Пловдив", 1912),
        ("Лудогорец Разград", "Разград", 1945),
        ("Черно море Варна", "Варна", 1913)
    ]
    
    created_clubs = []
    for name, city, founded_year in clubs:
        result = add_club(name)
        if "успешно" in result.lower():
            # Get the club ID
            club = execute_query("SELECT id FROM clubs WHERE name = ?", (name,), fetch=True)
            if club:
                created_clubs.append((club[0]['id'], name))
                print(f"[TEST SETUP] Created club: {name} (ID: {club[0]['id']})")
        else:
            print(f"[TEST SETUP] Club '{name}' already exists or error: {result}")
    
    return created_clubs

def create_test_players(clubs):
    """Create test players distributed among clubs"""
    players = [
        # Levski Sofia players
        (clubs[0][0], "Иван Иванов", "1995-03-15", "България", "GK", 1, "Активен"),
        (clubs[0][0], "Петър Петров", "1998-07-22", "България", "DF", 4, "Активен"),
        (clubs[0][0], "Мария Георгиева", "1997-11-08", "България", "MF", 10, "Активен"),
        (clubs[0][0], "Александър Николов", "1996-01-30", "България", "FW", 9, "Активен"),
        
        # CSKA Sofia players
        (clubs[1][0], "Георги Димитров", "1994-05-12", "България", "GK", 1, "Активен"),
        (clubs[1][0], "Николай Костов", "1999-09-18", "България", "DF", 3, "Активен"),
        (clubs[1][0], "Димитър Иванов", "1997-12-25", "България", "MF", 8, "Активен"),
        (clubs[1][0], "Кристиян Стоянов", "1998-04-03", "България", "FW", 11, "Активен"),
        
        # Botev Plovdiv players
        (clubs[2][0], "Мартин Камиларов", "1996-02-14", "България", "GK", 1, "Активен"),
        (clubs[2][0], "Илия Илиев", "1995-08-20", "България", "DF", 5, "Активен"),
        (clubs[2][0], "Радослав Стоянов", "1999-10-11", "България", "MF", 7, "Активен"),
        (clubs[2][0], "Васил Лечков", "1997-06-06", "България", "FW", 9, "Активен"),
        
        # Ludogorets players
        (clubs[3][0], "Владислав Стоянов", "1995-01-18", "България", "GK", 1, "Активен"),
        (clubs[3][0], "Калоян Стоянов", "1998-03-25", "България", "DF", 2, "Активен"),
        (clubs[3][0], "Ивелин Попов", "1996-07-14", "България", "MF", 6, "Активен"),
        (clubs[3][0], "Клавдиу Кейсел", "1997-12-01", "Румъния", "FW", 10, "Активен"),
        
        # Cherno More Varna players
        (clubs[4][0], "Димитър Манолов", "1994-11-22", "България", "GK", 1, "Активен"),
        (clubs[4][0], "Павел Вidanov", "1998-01-15", "България", "DF", 4, "Активен"),
        (clubs[4][0], "Атанас Пиров", "1996-09-30", "България", "MF", 8, "Активен"),
        (clubs[4][0], "Иван Стоянов", "1999-05-05", "България", "FW", 11, "Активен")
    ]
    
    for club_id, full_name, birth_date, nationality, position, number, status in players:
        result = add_player(
            club_id,
            full_name,
            birth_date,
            nationality,
            position,
            number,
            status
        )
        if "успешно" in result.lower():
            print(f"[TEST SETUP] Created player: {full_name} ({position}, #{number}) at club ID {club_id}")
        else:
            print(f"[TEST SETUP] Failed to create player {full_name}: {result}")

def main():
    print("=" * 60)
    print("FOOTBALL CHATBOT - TEST SETUP")
    print("=" * 60)
    
    # Initialize database
    initialize_database()
    print("[TEST SETUP] Database initialized")
    
    # Clear existing data
    clear_existing_data()
    
    # Create clubs
    print("\n[TEST SETUP] Creating test clubs...")
    clubs = create_test_clubs()
    print(f"[TEST SETUP] Created {len(clubs)} clubs")
    
    # Create players
    print("\n[TEST SETUP] Creating test players...")
    create_test_players(clubs)
    
    print("\n" + "=" * 60)
    print("TEST SETUP COMPLETE")
    print("=" * 60)
    
    # Show summary
    club_count = execute_query("SELECT COUNT(*) as count FROM clubs", fetch=True)
    player_count = execute_query("SELECT COUNT(*) as count FROM players", fetch=True)
    
    if club_count:
        print(f"Total clubs: {club_count[0]['count']}")
    if player_count:
        print(f"Total players: {player_count[0]['count']}")
    
    print("\nYou can now run the chatbot with: python src/main.py")
    print("Or test with: python test_setup.py (this script)")

if __name__ == "__main__":
    main()
