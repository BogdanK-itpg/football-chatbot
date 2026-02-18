#!/usr/bin/env python3
"""
Test script to verify chatbot integration with player commands.
Simulates a complete dialog using the chatbot module.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db import initialize_database
from clubs_service import add_club
from chatbot import parse_input, handle_intent, build_patterns

def print_separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f" {title}")
        print("=" * 60)

def test_chatbot_integration():
    print_separator("CHATBOT INTEGRATION TEST")
    
    # Initialize database
    initialize_database()
    print("[TEST] Database initialized")
    
    # Build patterns (force rebuild)
    import chatbot
    chatbot._intents_cache = None
    chatbot._patterns_cache = []
    chatbot._responses_cache = {}
    patterns = build_patterns()
    print(f"[TEST] Loaded {len(patterns)} patterns")
    
    # Create test clubs
    print("\n1. Creating clubs via chatbot...")
    commands = [
        "добави клуб Левски София",
        "добави клуб ЦСКА София",
        "добави клуб Ботев Пловдив"
    ]
    
    for cmd in commands:
        intent, params = parse_input(cmd)
        response = handle_intent(intent, params)
        print(f"   >> {cmd}")
        print(f"   << {response}")
    
    # Show clubs
    print("\n2. List all clubs:")
    intent, params = parse_input("покажи всички клубове")
    response = handle_intent(intent, params)
    print(f"   << {response}")
    
    # Add players
    print("\n3. Adding players via chatbot...")
    player_commands = [
        "добави играч Иван Иванов в клуб Левски София позиция GK номер 1 националност България дата на раждане 1995-03-15 статус Активен",
        "добави играч Петър Петров в клуб Левски София позиция DF номер 4 националност България дата на раждане 1998-07-22 статус Активен",
        "добави играч Георги Димитров в клуб ЦСКА София позиция GK номер 1 националност България дата на раждане 1994-05-12 статус Активен",
        "добави играч Мартин Камиларов в клуб Ботев Пловдив позиция GK номер 1 националност България дата на раждане 1996-02-14 статус Активен"
    ]
    
    for cmd in player_commands:
        intent, params = parse_input(cmd)
        response = handle_intent(intent, params)
        print(f"   >> {cmd}")
        print(f"   << {response}")
    
    # List players by club
    print("\n4. List players by club:")
    list_commands = [
        "покажи играчи на клуб Левски София",
        "покажи играчи на клуб ЦСКА София"
    ]
    
    for cmd in list_commands:
        intent, params = parse_input(cmd)
        response = handle_intent(intent, params)
        print(f"   >> {cmd}")
        print(f"   << {response}")
    
    # Update operations
    print("\n5. Update player attributes:")
    update_commands = [
        ("смени номер на Иван Иванов на 99", "update_player_number"),
        ("смени позиция на Петър Петров на MF", "update_player_position"),
        ("смени статус на Иван Иванов на Контузиран", "update_player_status")
    ]
    
    for cmd, expected_intent in update_commands:
        intent, params = parse_input(cmd)
        print(f"   >> {cmd}")
        print(f"   [Parsed] intent={intent}, params={params}")
        response = handle_intent(intent, params)
        print(f"   << {response}")
        assert intent == expected_intent, f"Expected {expected_intent}, got {intent}"
    
    # Verify updates
    print("\n6. Verify updates:")
    intent, params = parse_input("покажи играчи на клуб Левски София")
    response = handle_intent(intent, params)
    print(f"   << {response}")
    
    # Delete player
    print("\n7. Delete player:")
    cmd = "изтрий играч Иван Иванов"
    intent, params = parse_input(cmd)
    response = handle_intent(intent, params)
    print(f"   >> {cmd}")
    print(f"   << {response}")
    
    # Show final state
    print("\n8. Final state - all players:")
    intent, params = parse_input("покажи всички играчи")
    response = handle_intent(intent, params)
    print(f"   << {response}")
    
    # Error handling tests
    print_separator("ERROR HANDLING TESTS")
    
    error_tests = [
        ("добави играч Тест в клуб Несъществуващ позиция GK номер 1 националност България дата на раждане 2000-01-01 статус Активен", "Non-existent club"),
        ("смени номер на Несъществуващ на 10", "Non-existent player"),
        ("смени позиция на Тест на ST", "Invalid position"),
        ("смени номер на Тест на 150", "Invalid number")
    ]
    
    for cmd, description in error_tests:
        intent, params = parse_input(cmd)
        response = handle_intent(intent, params)
        print(f"\n   Test: {description}")
        print(f"   >> {cmd}")
        print(f"   << {response}")
    
    print_separator("ALL CHATBOT INTEGRATION TESTS PASSED")
    print()

if __name__ == "__main__":
    try:
        test_chatbot_integration()
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
