# Football League Chatbot (futbolche)

A command-line chatbot for managing football leagues, clubs, players, matches, and statistics. Built with Python and SQLite.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation & Setup](#installation--setup)
5. [Usage](#usage)
6. [Example Dialogue](#example-dialogue)
7. [Round-Robin Algorithm](#round-robin-algorithm)
8. [Testing](#testing)
9. [Maintenance](#maintenance)
10. [Known Issues](#known-issues)
11. [Future Enhancements](#future-enhancements)
12. [License](#license)

---

## Overview

**futbolche** is a text-based conversational interface for managing football league data. Users interact with the system using natural Bulgarian language commands to perform CRUD operations on clubs, players, matches, and leagues, and to retrieve statistics.

### Purpose

- Provide an intuitive, conversational interface for football data management
- Demonstrate NLU (Natural Language Understanding) pattern matching
- Serve as a learning project for database-driven applications
- Enable quick data entry and querying without complex forms

### Technology Stack

- **Language:** Python 3.x
- **Database:** SQLite 3
- **Architecture:** Layered (NLU → Router → Services → Repositories → Database)
- **Pattern Matching:** Regex-based intent classification
- **Storage:** File-based SQLite database (`sql/football.db`)

---

## Features

### Club Management
- Create, list, update, and delete football clubs
- Store club name, city, and founding year
- Cascade deletion of associated players

### Player Management
- Register players with full details (name, position, number, nationality, birth date, status)
- Validate positions (GK, DF, MF, FW) and jersey numbers (1-99)
- Update player position, number, and status
- List players by club or all players
- Delete players

### Match Management
- Record matches with teams, date, and final score
- View match details
- Log in-game events (goals, assists, cards, appearances)
- Auto-update match score when first goal is recorded

### League Management
- Create leagues with name and season (validated format: `2025`, `2025/26`, `2025/2026`)
- Add clubs to leagues (duplicate prevention)
- Remove clubs from leagues (blocked if schedule already generated)
- Generate round-robin fixtures (single or double round-robin)
- View league standings with automatic points calculation (3/1/0 system)
- List teams in a league (shows club name and ID)
- View all fixtures for a league

### Statistics & Analytics
- Club statistics: matches played, wins/draws/losses, goals for/against, points
- Player statistics: goals, assists, appearances, cards
- Advanced player metrics: goals per 90, assists per 90 (approximated)

### Transfers
- Transfer players between clubs
- Atomic transactions with rollback on errors
- Automatic jersey number reassignment if conflict in destination club
- Transfer logging

### Natural Language Interface
- Bulgarian language commands (with some English alternatives)
- Multiple pattern variations per intent
- Parameter extraction from user input
- Context-aware error messages
- All commands logged to `commands.log` with timestamp, intent, status

---

## Architecture

### Project Structure

```
futbolche/
├── src/
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── chatbot.py          # parse_and_handle() — entry point for NLU + routing
│   │   ├── nlu.py              # Pattern matching engine (_pattern_to_regex)
│   │   ├── router.py           # Intent routing + logging wrapper
│   │   └── intents.json        # Intent definitions, patterns, examples (28 intents)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── clubs_service.py
│   │   ├── players_service.py
│   │   ├── matches_service.py
│   │   ├── leagues_service.py  # Business logic: round-robin, standings, fixtures
│   │   ├── statistics_service.py
│   │   └── transfers_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── clubs_repo.py       # Clubs SQL queries
│   │   ├── players_repo.py     # Players SQL queries
│   │   ├── matches_repo.py     # Matches SQL queries + self-match guard
│   │   ├── leagues_repo.py     # Leagues + league_teams SQL queries
│   │   └── events_repo.py      # Events SQL queries
│   ├── handlers/
│   │   └── handler_matches.py  # Match command handlers (show_round, save_result, etc.)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py           # Command logging (append to commands.log)
│   ├── validators.py           # Match event validation helpers
│   ├── state.py                # Current match context management
│   ├── db.py                   # Database connection, execute_query, fetch_all, fetch_one
│   └── main.py                 # CLI entry point
├── sql/
│   ├── schema.sql              # Full database schema with all constraints
│   └── migration.sql           # Migration script for existing databases
├── tests/
│   ├── test_leagues_service.py # 18 league service tests
│   ├── test_integration_all_intents.py  # NLU + end-to-end integration
│   ├── test_matches_events.py
│   ├── test_clubs_service.py
│   └── test_config.py          # Test database environment setup
├── docs/
│   └── README.md
├── commands.log                 # Command history log (auto-created)
└── requirements.txt
```

### Layers

```
User Input (Bulgarian)
       │
       ▼
┌─────────────────┐
│   chatbot.py     │  parse_and_handle() → returns response string
│   (NLU layer)    │  Internal: parse_input() → intent + params
└────────┬────────┘
         │ intent tag + params dict
         ▼
┌─────────────────┐
│   router.py      │  handle_intent() routes to service functions
│   (Routing)      │  Wraps every call with log_command()
└────────┬────────┘
         │
         ├──→ clubs_service.py
         ├──→ players_service.py
         ├──→ matches_service.py
         ├──→ leagues_service.py     ←── Business logic layer
         ├──→ statistics_service.py
         └──→ transfers_service.py
                 │
                 ▼
         ┌─────────────────┐
         │  repositories/   │  Data access layer — only code that
         │  *_repo.py       │  constructs SQL queries
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   db.py          │  execute_query(), fetch_all(), fetch_one()
         │   (SQLite)       │  Connection management, parameterized queries
         └─────────────────┘
```

### Data Flow

1. **Input:** User types command in Bulgarian
2. **NLU Layer** (`chatbot.py` → `nlu.py`): Parses input, matches against patterns in `intents.json` (sequential first-match-wins), extracts parameters, returns `(intent_tag, params_dict)`
3. **Router** (`router.py`): Receives `(intent, params, raw_input)`, validates required parameters, calls appropriate service function, then logs the command with timestamp, intent, status (OK/ERROR), and raw input
4. **Services** (`services/*.py`): Pure business logic — validation, algorithm execution, orchestrating multiple repository calls
5. **Repositories** (`repositories/*_repo.py`): One function per SQL query — constructs parameterized queries, calls `db.py` helpers
6. **Database** (`db.py`): Low-level SQL execution, connection pooling, `sqlite3.Row` result wrapping
7. **Response:** Service returns result string → Router passes through → Printed to user

### Database Schema

**Tables:**

| Table | Fields | Constraints |
|---|---|---|
| `clubs` | `id`, `name`, `city`, `founded_year` | `UNIQUE(name)` |
| `players` | `id`, `club_id`, `full_name`, `birth_date`, `nationality`, `position`, `number`, `status` | `FK(club_id)`, `CHECK(position IN ('GK','DF','MF','FW'))` |
| `leagues` | `id`, `name`, `season`, `created_at` | `UNIQUE(name, season)`, `created_at DEFAULT datetime('now')` |
| `league_teams` | `id`, `league_id`, `club_id`, `joined_at` | `UNIQUE(league_id, club_id)`, `FK(league_id)`, `FK(club_id)`, `joined_at DEFAULT datetime('now')` |
| `matches` | `id`, `home_team_id`, `away_team_id`, `home_goals`, `away_goals`, `match_date`, `league_id`, `round_no`, `is_played` | `UNIQUE(league_id, round_no, home_team_id, away_team_id)`, `FK(home_team_id)`, `FK(away_team_id)`, `FK(league_id)` |
| `events` | `id`, `match_id`, `player_id`, `club_id`, `event_type`, `card_type`, `minute`, `is_own_goal`, `created_at` | `FK(match_id)`, `FK(player_id)`, `FK(club_id)`, `CHECK(event_type IN (...))` |

**Key constraints:**
- Self-match prevention: `matches_repo.create()` returns `None` if `home_team_id == away_team_id`
- Duplicate leagues: prevented by `UNIQUE(name, season)` + Python check in `create_league()`
- Duplicate league teams: prevented by `UNIQUE(league_id, club_id)` at DB level
- Duplicate matches: prevented by `UNIQUE(league_id, round_no, home_team_id, away_team_id)`
- All foreign keys use `ON DELETE CASCADE` (except `events` uses `SET NULL` for player_id and club_id)

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. **Clone or download the repository:**
   ```bash
   cd d:/Projects/football-chatbot/futbolche
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   If `requirements.txt` doesn't exist, the project has no external dependencies beyond Python standard library.

3. **Initialize the database:**
   The database auto-initializes on first run. The `sql/schema.sql` file will be executed automatically when `main.py` starts.

   To manually initialize:
   ```bash
   python -c "from db import initialize_database; initialize_database()"
   ```

### Running the Application

```bash
python src/main.py
```

You'll see:
```
Football League Chatbot
Напишете 'помощ' за команди.
>>
```

Type commands in Bulgarian (or English where supported) and press Enter.

---

## Usage Guide

### Command Syntax

All commands follow the pattern:
```
[action] [entity] [parameters]
```

**Examples:**
- `добави клуб Левски` → action=добави, entity=клуб, parameter=Левски
- `покажи статистика на клуб Левски` → action=покажи, entity=статистика, target=клуб Левски

### Parameters

- **Identifiers** (club, player, match, league): Can be name (case-insensitive) or numeric ID
- **Dates**: YYYY-MM-DD format (e.g., `2025-03-15`)
- **Positions**: `gk`, `df`, `mf`, `fw` (case-insensitive in NLU, validated lowercase)
- **Season formats**: `2025`, `2025/26`, `2025/2026`, `2025-2026`
- **Numbers**: Integers 1-99 for jersey numbers
- **Event types**: `гол`, `асист`, `жълт картон`, `червен картон`, `поява`

### Getting Help

Type `помощ` to see all available command patterns.

### Error Handling

The chatbot provides Bulgarian error messages for common issues:
- Missing parameters
- Validation failures
- Non-existent entities
- Constraint violations
- Duplicate prevention

If a command fails, review the error message and adjust your input accordingly.

---

## Example Dialogue

### Full League Lifecycle

```
>> създай лига Първа Лига 2025/26
Лига 'Първа Лига' (2025/26) беше създадена успешно.

>> добави клуб Левски София в лига Първа Лига
Клубът беше добавен в лигата успешно.

>> добави клуб ЦСКА София в лига Първа Лига
Клубът беше добавен в лигата успешно.

>> добави клуб Ботев Пловдив в лига Първа Лига
Клубът беше добавен в лигата успешно.

>> добави клуб Лудогорец Разград в лига Първа Лига
Клубът беше добавен в лигата успешно.

>> покажи отбори в лига Първа Лига
- Левски София (ID: 1)
- ЦСКА София (ID: 2)
- Ботев Пловдив (ID: 3)
- Лудогорец Разград (ID: 4)

>> генерирай кръгове за лига Първа Лига
Създадени 12 мача за лига Първа Лига.

>> покажи класиране Първа Лига
Няма мачове в тази лига.

>> запиши мач Левски София срещу ЦСКА София дата 2025-09-01 резултат 2-1
Мачът беше записан.

>> запиши мач Ботев Пловдив срещу Лудогорец Разград дата 2025-09-01 резултат 0-0
Мачът беше записан.

>> покажи класиране Първа Лига
1. Левски София | P:1 W:1 D:0 L:0 GF:2 GA:1 GD:1 Pts:3
2. Ботев Пловдив | P:1 W:0 D:1 L:0 GF:0 GA:0 GD:0 Pts:1
3. Лудогорец Разград | P:1 W:0 D:1 L:0 GF:0 GA:0 GD:0 Pts:1
4. ЦСКА София | P:1 W:0 D:0 L:1 GF:1 GA:2 GD:-1 Pts:0
```

### Club and Player Management

```
>> добави клуб Левски София
Клубът беше добавен успешно.

>> добави клуб Левски София
Клуб с това име вече съществува.

>> покажи всички клубове
Левски София
ЦСКА София
...

>> добави играч Иван Иванов в клуб 1 позиция GK номер 1 националност България дата на раждане 1995-03-15 статус Активен
Играчът беше добавен успешно.

>> изтрий играч Иван Иванов
Играчът беше изтрит.

>> редактирай клуб Левски София на Левски 1914
Клубът беше обновен.
```

### League Edge Cases

```
>> създай лига Дублираща 2025
Лига 'Дублираща' (2025) беше създадена успешно.

>> създай лига Дублираща 2025
Лига с име 'Дублираща' и сезон '2025' вече съществува.

>> премахни отбор Левски София от лига Първа Лига
Не можете да премахнете отбор, след като програмата е генерирана. Изтрийте програмата първо.

>> генерирай кръгове за лига Първа Лига
Програмата за тази лига вече е генерирана.

>> добави клуб Несъществуващ Клуб в лига Първа Лига
Клубът не съществува.

>> покажи класиране Несъществуваща Лига
Няма лига с име/ID 'Несъществуваща Лига'.

>> покажи мачове в лига Първа Лига
2025-09-01: Левски София vs ЦСКА София (2-1)
2025-09-01: Ботев Пловдив vs Лудогорец Разград (0-0)
```

### Help and Navigation

```
>> помощ
Налични команди:

Клубове:
- добави клуб [club_name]
- покажи всички клубове
- промени клуб [club_name] на [new_name]
- изтрий клуб [club_name]

Играчи:
- добави играч [full_name] в клуб [club_identifier] позиция [position] номер [number] ...
- покажи играчи на клуб [club_identifier]
- покажи всички играчи
- смени позиция на [player_identifier] на [new_position]
- смени номер на [player_identifier] на [new_number]
- смени статус на [player_identifier] на [new_status]
- изтрий играч [player_identifier]
- трансферирай играч [player_identifier] в клуб [club_identifier]

Статистика:
- покажи статистика на клуб [club_identifier]
- покажи статистика на играч [player_identifier]
- покажи метрики на играч [player_identifier]

Мачове:
- запиши мач [home_team] срещу [away_team] дата [match_date] резултат [home_goals]-[away_goals]
- покажи мач [match_id]
- запиши гол [player_identifier] в мач [match_id] минута [minute]
- запиши асист [player_identifier] в мач [match_id] минута [minute]
- запиши жълт картон [player_identifier] в мач [match_id] минута [minute]
- запиши червен картон [player_identifier] в мач [match_id] минута [minute]
- запиши поява [player_identifier] в мач [match_id]
- покажи мачове в лига [league_identifier]
- покажи кръг [round_no] [league_name] [season]
- резултат [home_team]-[away_team] [home_goals]:[away_goals] запиши
- гол [player_name] [team_name] [minute] минута
- картон [player_name] [team_name] [card_type] [minute]
- избери мач [match_id]
- покажи събития [match_id]

Лиги:
- създай лига [league_name] [season]
- добави клуб [club_identifier] в лига [league_identifier]
- премахни отбор [club_identifier] от лига [league_identifier]
- покажи отбори в лига [league_identifier]
- генерирай кръгове за лига [league_identifier]
- покажи класиране [league_identifier]
- покажи мачове в лига [league_identifier]

Други:
- изход (затвори чатбота)
- помощ (покажи тази помощ)
```

---

## Round-Robin Algorithm

The schedule generator uses the **Circle Method** (also known as the "Polygon Method" or "Berger Tables"), a mathematically proven algorithm for constructing a complete round-robin tournament schedule.

### How It Works

1. **Fix one team** in position. Place all other teams in a rotating list.
2. For each round, pair the fixed team against the last team in the rotating list, then pair the remaining teams symmetrically (first vs second-to-last, second vs third-to-last, etc.).
3. After each round, rotate the list by moving the last element to the front.
4. After all rounds are complete, every team has played every other team exactly once.

### Even Number of Teams (N)

```
For N teams:
  Rounds = N - 1
  Matches = N × (N - 1) / 2
  Matches per round = N / 2
  Every team plays exactly once per round
```

**Example with 4 teams (A, B, C, D):**

```
Round 1:    A vs D    B vs C
Round 2:    A vs C    D vs B    (rotation: D moves to front)
Round 3:    A vs B    C vs D    (rotation: B moves to front)
```

Total: 3 rounds, 6 matches, every pair appears once.

### Odd Number of Teams (N)

When N is odd, a **BYE placeholder** is added to make the count even. The team paired with BYE rests that round.

```
Rounds = N  (each team gets one rest round)
Matches = N × (N - 1) / 2
```

**Example with 3 teams (A, B, C):**

```
Round 1:    A vs C    B (BYE)
Round 2:    A vs B    C (BYE)
Round 3:    B vs C    A (BYE)
```

Total: 3 rounds, 3 matches, each team rests once.

### Home/Away Assignment

Home/away status alternates between rounds:
- For the fixed-team match: home = fixed team on odd rounds, away on even rounds
- For rotating pairs: away = the first-listed team on even rounds, home on odd rounds
- This ensures balanced home/away distribution

### Double Round-Robin

If `double_round=True`, the entire schedule is generated twice:
- First pass: standard round-robin (each pair once)
- Second pass: same rotation but with inverted home/away
- Total matches = N × (N - 1)
- Total rounds = 2 × (N - 1)

### Implementation

The algorithm is implemented in `src/services/leagues_service.py:generate_round_robin()`:
- Lines 77-84: Setup and BYE handling
- Lines 87-104: `_schedule_round()` inner function — pairs teams, assigns home/away, inserts matches
- Lines 106-108: Main loop over all rounds, rotates after each
- Lines 110-113: Double round-robin pass
- Lines 62-64: Regeneration prevention (checks existing matches before generating)

### Verified Properties

The algorithm passes test scenarios for:
- **4 teams**: 6 matches, 3 rounds, 2 matches/round, every team plays once/round
- **3 teams**: 3 matches, 3 rounds, BYE each round
- **Regeneration blocked**: second call returns error message
- **Too few teams (<2)**: rejected with error message
- **Self-match prevention**: guarded at repository level

---

## Testing

### Test Suite

The project includes comprehensive tests:

- **League Service Tests** (18 tests): Create league, duplicates, season validation, add/remove teams, round-robin generation, standings, fixtures, self-match prevention
- **Integration Tests** (78 tests): End-to-end workflows, NLU pattern matching across all 28 intents
- **Club Service Tests** (20 tests): CRUD operations, database error handling
- **Match Events Tests** (2 tests): Standings computation, event recording

### Running Tests

```bash
# Run all tests
python -m pytest -v

# Run only league service tests
python -m pytest tests/test_leagues_service.py -v

# Run integration tests
python -m pytest tests/test_integration_all_intents.py -v

# Run specific test module
python -m pytest tests/test_clubs_service.py -v
```

---

## Maintenance

### Database Maintenance

**Backup:**
```bash
copy sql\football.db sql\football_backup.db
```

**Reset Database:**
```bash
del sql\football.db
python -c "from db import initialize_database; initialize_database()"
```

**Vacuum (optimize):**
```bash
python -c "from db import execute; execute('VACUUM')"
```

### Logging

Command history is logged to `commands.log` via `utils/logger.py`. Each entry includes:
- ISO 8601 UTC timestamp
- Intent name (right-padded to 15 chars)
- Status (OK or ERROR)
- Raw user input
- Error reason (if applicable)

Logs are appended and never truncated.

### Adding New Intents

1. Define intent in `src/chatbot/intents.json`:
   ```json
   {
     "tag": "new_intent",
     "patterns": ["pattern 1", "pattern 2"],
     "responses": ["Response message"],
     "examples": ["pattern 1"]
   }
   ```

2. Add routing logic in `src/chatbot/router.py`:
   ```python
   if intent == 'new_intent':
       # Validate params
       # Call service function
       return result
   ```

3. Implement service function in appropriate `src/services/*.py` file.

4. Add repository function in appropriate `src/repositories/*_repo.py` file.

5. Add tests in `tests/` directory.

### Code Style

- Follow PEP 8 guidelines
- Use type hints on function signatures
- Include docstrings for complex functions
- Services call repositories; repositories call db.py — never skip layers
- Keep services independent (no direct imports between service modules)

---

## Known Issues

### 1. Season Format Validation (Low Priority)

The regex `^\d{4}([\/-]\d{2,4})?$` validats `2025/26` but rejects `2025-2026`. All formats `2025`, `2025/26`, `2025/2026`, and `2025-2026` are accepted.

### 2. `execute_query` Returns `None` for Empty Results

The `execute_query()` function in `db.py` returns `None` instead of `[]` when `fetch=True` and no rows match. This causes `TypeError: object of type 'NoneType' has no len()` in some integration tests. The `fetch_all()` function correctly returns `[]`.

### 3. No Transaction Rollback in Service Layer

The `db.py` module has a `rollback()` function but it is never called in the service layer. All database operations auto-commit after each `execute()` call. Multi-step operations that fail mid-way may leave partial data.

### 4. Encoding Issues

Bulgarian text in error messages may display incorrectly in Windows console (code page mismatch). This is cosmetic and doesn't affect functionality. Tests use encoding-agnostic comparisons to mitigate.

---

## Future Enhancements

### Short-term
- [ ] Add explicit transaction handling with rollback in service layer
- [ ] Fix `execute_query()` to return `[]` instead of `None` for empty results
- [ ] Add case-insensitive position validation in player service
- [ ] Add fuzzy matching for typos in user input
- [ ] Add intent confidence scores with fallback to `unknown`

### Medium-term
- [ ] Support date ranges for match queries
- [ ] Add player search by nationality/position
- [ ] Implement match result editing
- [ ] Add league season management (start/end dates)
- [ ] Export statistics to CSV/JSON

### Long-term
- [ ] Web interface (Flask/Django)
- [ ] REST API layer
- [ ] Multi-user support with authentication
- [ ] Real-time match updates
- [ ] Mobile app frontend
- [ ] Integration with external football data APIs

---

## License

[Specify license here - e.g., MIT, GPL, etc.]

---

## Contact

For questions, issues, or feedback, please open an issue on the project repository.

---

**Project Version:** 1.0
**Last Updated:** 2026-06-06
