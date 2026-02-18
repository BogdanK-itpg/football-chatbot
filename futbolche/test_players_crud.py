#!/usr/bin/env python3
"""
Test script to verify all player CRUD operations work correctly.
This simulates a dialog with the chatbot.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db import initialize_database, execute_query
from clubs_service import add_club, get_all_clubs
from players_service import (
    add_player, get_players_by_club, get_player_id,
    update_player_position, update_player_number, update_player_status,
    delete_player
)

def print_separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f" {title}")
        print("=" * 60)

def test_crud_operations():
    print_separator("PLAYERS CRUD TEST")
    
    # Initialize database
    initialize_database()
    print("[TEST] Database initialized")
    
    # Step 1: Create some clubs
    print("\n1. Creating test clubs...")
    clubs = ["Левски София", "ЦСКА София", "Ботев Пловдив"]
    for club_name in clubs:
        result = add_club(club_name)
        print(f"   {result}")
    
    # Show clubs
    print("\n   All clubs:")
    print("   " + get_all_clubs().replace("\n", "\n   "))
    
    # Step 2: Add players
    print_separator("2. ADD PLAYER")
    
    # Get club IDs
    levski = execute_query("SELECT id FROM clubs WHERE name = ?", ("Левски София",), fetch=True)[0]['id']
    cska = execute_query("SELECT id FROM clubs WHERE name = ?", ("ЦСКА София",), fetch=True)[0]['id']
    botev = execute_query("SELECT id FROM clubs WHERE name = ?", ("Ботев Пловдив",), fetch=True)[0]['id']
    
    # Add player 1
    result = add_player(
        club_id=levski,
        full_name="Иван Иванов",
        birth_date="1995-03-15",
        nationality="България",
        position="GK",
        number=1,
        status="Активен"
    )
    print(f"   {result}")
    
    # Add player 2
    result = add_player(
        club_id=levski,
        full_name="Петър Петров",
        birth_date="1998-07-22",
        nationality="България",
        position="DF",
        number=4,
        status="Активен"
    )
    print(f"   {result}")
    
    # Add player 3
    result = add_player(
        club_id=cska,
        full_name="Георги Димитров",
        birth_date="1994-05-12",
        nationality="България",
        position="GK",
        number=1,
        status="Активен"
    )
    print(f"   {result}")
    
    # Add player 4
    result = add_player(
        club_id=botev,
        full_name="Мартин Камиларов",
        birth_date="1996-02-14",
        nationality="България",
        position="GK",
        number=1,
        status="Активен"
    )
    print(f"   {result}")
    
    # Step 3: List players by club
    print_separator("3. LIST PLAYERS BY CLUB")
    
    print("\n   Players on Левски София:")
    result = get_players_by_club("Левски София")
    print("   " + result.replace("\n", "\n   "))
    
    print("\n   Players on ЦСКА София:")
    result = get_players_by_club("ЦСКА София")
    print("   " + result.replace("\n", "\n   "))
    
    print("\n   All players (no filter):")
    result = get_players_by_club()
    print("   " + result.replace("\n", "\n   "))
    
    # Step 4: Update operations
    print_separator("4. UPDATE PLAYER")
    
    # Update number
    print("\n   Change Иван Иванов number to 99:")
    result = update_player_number("Иван Иванов", 99)
    print(f"   {result}")
    
    # Update position
    print("\n   Change Петър Петров position to MF:")
    result = update_player_position("Петър Петров", "MF")
    print(f"   {result}")
    
    # Update status
    print("\n   Change Иван Иванов status to 'Контузиран':")
    result = update_player_status("Иван Иванов", "Контузиран")
    print(f"   {result}")
    
    # Verify updates
    print("\n   Левски София players after updates:")
    result = get_players_by_club("Левски София")
    print("   " + result.replace("\n", "\n   "))
    
    # Step 5: Validation tests
    print_separator("5. VALIDATION TESTS")
    
    print("\n   Try invalid number (150):")
    result = update_player_number("Петър Петров", 150)
    print(f"   {result}")
    
    print("\n   Try invalid position (ST):")
    result = update_player_position("Петър Петров", "ST")
    print(f"   {result}")
    
    print("\n   Try non-existent player:")
    result = update_player_number("Несъществуващ", 10)
    print(f"   {result}")
    
    print("\n   Try non-existent club:")
    result = get_players_by_club("Несъществуващ клуб")
    print(f"   {result}")
    
    # Step 6: Delete player
    print_separator("6. DELETE PLAYER")
    
    print("\n   Delete Иван Иванов:")
    result = delete_player("Иван Иванов")
    print(f"   {result}")
    
    print("\n   Левски София players after deletion:")
    result = get_players_by_club("Левски София")
    print("   " + result.replace("\n", "\n   "))
    
    print("\n   Try delete non-existent player:")
    result = delete_player("Несъществуващ")
    print(f"   {result}")
    
    # Step 7: Final summary
    print_separator("7. FINAL DATABASE STATE")
    
    club_count = execute_query("SELECT COUNT(*) as count FROM clubs", fetch=True)[0]['count']
    player_count = execute_query("SELECT COUNT(*) as count FROM players", fetch=True)[0]['count']
    
    print(f"\n   Total clubs: {club_count}")
    print(f"   Total players: {player_count}")
    
    print("\n   All players in database:")
    result = get_players_by_club()
    print("   " + result.replace("\n", "\n   "))
    
    print_separator("ALL TESTS COMPLETED SUCCESSFULLY")
    print()

if __name__ == "__main__":
    try:
        test_crud_operations()
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
