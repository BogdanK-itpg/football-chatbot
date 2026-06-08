#!/usr/bin/env python3
"""Test all chatbot commands via NLU + router pipeline."""

import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ===== Setup test database =====
import db as real_db
tmpdir = tempfile.mkdtemp()
real_db.DB_PATH = os.path.join(tmpdir, 'test_football.db')
real_db.initialize_database()

from chatbot.router import handle_intent, CATEGORIES
from chatbot.nlu import parse_input


def test(description, cmd, expected_keywords=None, not_expected=None):
    try:
        intent, params = parse_input(cmd)
        response = handle_intent(intent, params or {}, raw_input=cmd)
        ok = True
        msg = response.replace('\n', ' | ')
        if expected_keywords:
            for kw in expected_keywords:
                if kw.lower() not in response.lower():
                    ok = False
                    break
        if not_expected:
            for kw in not_expected:
                if kw.lower() in response.lower():
                    ok = False
                    break
        status = 'PASS' if ok else 'FAIL'
        print(f"  [{status}] {description}")
        if not ok:
            print(f"         Expected: {expected_keywords}")
            print(f"         Got: {msg[:120]}")
        return ok
    except Exception as e:
        print(f"  [FAIL] {description} -> {type(e).__name__}: {str(e)[:100]}")
        return False


# ===== Setup test data =====
print("Setting up test data...")
from services.clubs_service import add_club
add_club("Левски София")
add_club("ЦСКА София")
add_club("Ботев Пловдив")
add_club("Лудогорец Разград")

from services.leagues_service import create_league, add_club_to_league
from repositories import leagues_repo
create_league("Първа Лига", "2025/2026")
lid = leagues_repo.resolve_id("Първа Лига")
for name in ["Левски София", "ЦСКА София", "Ботев Пловдив", "Лудогорец Разград"]:
    add_club_to_league(lid, name)

from services.matches_service import record_match
for i in range(1, 11):
    record_match("Левски София", "ЦСКА София", f"2025-{i:02d}-01",
                 home_goals=2, away_goals=1, league_id=lid)
    record_match("Лудогорец Разград", "Ботев Пловдив", f"2025-{i:02d}-02",
                 home_goals=1, away_goals=0, league_id=lid)
    record_match("ЦСКА София", "Ботев Пловдив", f"2025-{i:02d}-03",
                 home_goals=1, away_goals=1, league_id=lid)
    record_match("Левски София", "Лудогорец Разград", f"2025-{i:02d}-04",
                 home_goals=1, away_goals=2, league_id=lid)

# Player for player commands
from services.players_service import add_player
from repositories import clubs_repo
levski = clubs_repo.get_by_name("Левски София")
if levski:
    add_player(levski['id'], "Тест Играч", "1990-01-01", "България", "FW", 9, "Активен")

# ===== Run all commands =====
print("\n=== HELP ===")
intent, params = parse_input("помощ")
response = handle_intent(intent, params, raw_input="помощ")
print(response[:600])

print("\n=== CATEGORIES AND TAG COVERAGE ===")
# Verify predict_match is in CATEGORIES
all_tags = {t for tags in CATEGORIES.values() for t in tags}
print(f"Tags registered in CATEGORIES: {len(all_tags)}")

# Verify all intents have a matching tag
with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'chatbot', 'intents.json'), encoding='utf-8') as f:
    intents_data = json.load(f)
all_intent_tags = {i['tag'] for i in intents_data['intents']}
missing_from_categories = all_intent_tags - all_tags
if missing_from_categories:
    print(f"WARNING: Tags not in CATEGORIES: {missing_from_categories}")
else:
    print("OK: All intents are registered in CATEGORIES")

print("\n=== COMMAND TESTS ===\n")

# Help
test("помощ", "помощ", expected_keywords=["Prediction"])

# Clubs
test("покажи клубове", "покажи клубове", expected_keywords=["Левски", "ЦСКА"])
test("добави клуб", "добави клуб Нов Клуб", expected_keywords=["добавен"])
test("добави клуб (дублиране)", "добави клуб Нов Клуб", expected_keywords=["вече съществува"])
test("редактирай клуб", "редактирай клуб Нов Клуб на Оновен Клуб", expected_keywords=["обновен"])
test("изтрий клуб", "изтрий клуб Оновен Клуб", expected_keywords=["изтрит"])
test("покажи клубове (няма)", "покажи клубове", expected_keywords=["Левски"])

# Leagues
test("създай лига", "създай лига Нова Лига сезон 2025", expected_keywords=["създадена"])
test("добави клуб в лига", "добави клуб Левски София в лига Нова Лига", expected_keywords=["добавен"])
test("отбори в лига", "покажи отбори в лига Първа Лига", expected_keywords=["Левски"])
test("генерирай кръгове", "генерирай кръгове за лига Нова Лига", expected_keywords=["създадени"])

# Players
test("добави играч", "добави играч Друг Играч в клуб Левски София позиция MF номер 7 националност България дата на раждане 1995-06-15 статус Активен", expected_keywords=["добавен"])
test("покажи играчи", "покажи играчи на клуб Левски София", not_expected=["Няма"])
test("покажи всички играчи", "покажи всички играчи", not_expected=["Няма"])

# Standings
test("класиране", "покажи класиране Първа Лига", expected_keywords=["1.", "MP", "PTS"])

# Matches
test("запиши мач", "запиши мач Левски София срещу ЦСКА София дата 2025-11-01 резултат 3-1", expected_keywords=["записан"])
test("покажи мач", "покажи мач 1", not_expected=["грешка"])
test("избери мач", "избери мач 1", expected_keywords=["избран"])
test("покажи кръг", "покажи кръг 1 Първа Лига", not_expected=["Няма"])

# AI Prediction
test("Prediction EN", "Prediction Левски София vs Лудогорец Разград", expected_keywords=["%"])
test("Predict EN", "Predict Левски София vs Лудогорец Разград", expected_keywords=["%"])
test("Прогноза BG", "Прогноза Левски София срещу Лудогорец Разград", expected_keywords=["%"])
test("Predict against", "Predict Левски София against Лудогорец Разград", expected_keywords=["%"])

# AI Edge cases
test("Prediction грешен отбор", "Prediction НЕсъществуващ vs Лудогорец Разград", expected_keywords=["Team does not exist"])

# Test the help shows prediction
print("\n=== HELP PREDICTION CHECK ===")
intent, params = parse_input("помощ")
response = handle_intent(intent, params, raw_input="помощ")
if "Prediction" in response:
    print("PASS: help shows Prediction command")
else:
    print("FAIL: help does not show Prediction command")
    # Find what's in the matche category
    for line in response.split('\n'):
        if 'Prediction' in line:
            print(f"  Found: {line.strip()}")

print("\n=== SUMMARY ===")
print(f"Test DB: {tmpdir}")

# Cleanup
shutil.rmtree(tmpdir)
