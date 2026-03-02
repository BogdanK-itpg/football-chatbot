#!/usr/bin/env python3
"""Quick test to identify NLU pattern matching issues"""

import sys
sys.path.insert(0, 'src')
from chatbot.nlu import parse_input

tests = [
    ("помощ", "help"),
    ("изход", "exit"),
    ("добави клуб Нови Клуб", "add_club"),
    ("покажи всички клубове", "list_clubs"),
    ("изтрий клуб Левски", "delete_club"),
    ("изтрий играч Иван", "delete_player"),
    ("редактирай клуб Левски на Нови", "update_club"),
    ("добави играч Иван в клуб Левски позиция GK номер 1 националност България дата на раждане 1995-03-15 статус Активен", "add_player"),
    ("покажи играчи на клуб Левски", "list_players"),
    ("покажи всички играчи", "list_all_players"),
    ("смени позиция на Иван на GK", "update_player_position"),
    ("смени номер на Иван на 10", "update_player_number"),
    ("смени статус на Иван на Активен", "update_player_status"),
    ("покажи статистика на клуб Левски", "club_statistics"),
    ("покажи статистика на играч Иван", "player_statistics"),
    ("покажи метрики на играч Иван", "player_metrics"),
    ("трансферирай играч Иван в клуб ЦСКА", "transfer_player"),
    ("запиши мач Левски срещу ЦСКА дата 2025-09-01 резултат 2-1", "record_match"),
    ("покажи мач 1", "show_match"),
    ("създай лига Нова Лига сезон 2025", "create_league"),
    ("добави клуб Левски в лига Нова Лига", "add_club_to_league"),
    ("покажи отбори в лига Нова Лига", "get_league_teams"),
    ("генерирай кръгове за лига Нова Лига", "generate_round_robin"),
    ("покажи класиране Нова Лига", "get_standings"),
    ("запиши гол Иван в мач 1 минута 23", "record_event"),
    ("покажи мачове в лига Нова Лига", "get_fixtures"),
]

print("Testing NLU pattern matching:")
print("=" * 60)
failures = []
for inp, expected in tests:
    result, params = parse_input(inp)
    status = "PASS" if result == expected else "FAIL"
    if result != expected:
        failures.append((inp, expected, result))
    print(f"{status}: '{inp[:40]}...' -> expected {expected}, got {result}")

print("\n" + "=" * 60)
if failures:
    print(f"FAILED: {len(failures)}/{len(tests)} tests failed")
    for inp, exp, got in failures:
        print(f"  Expected {exp} but got {got} for: {inp[:50]}")
else:
    print(f"SUCCESS: All {len(tests)} tests passed!")
