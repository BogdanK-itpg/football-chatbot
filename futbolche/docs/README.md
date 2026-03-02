# Football League Chatbot (futbolche)

A command-line chatbot for managing football leagues, clubs, players, matches, and statistics. Built with Python and SQLite.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation & Setup](#installation--setup)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Maintenance](#maintenance)
8. [Known Issues](#known-issues)
9. [Future Enhancements](#future-enhancements)
10. [License](#license)

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
- **Architecture:** Layered (NLU → Router → Services → Database)
- **Pattern Matching:** Regex-based intent classification
- **Storage:** File-based SQLite database (`sql/futbolche.db`)

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
- Create leagues with name and season
- Add clubs to leagues
- Generate round-robin fixtures (single or double)
- View league standings with automatic calculation
- List teams in a league
- View all fixtures

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

---

## Architecture

### Project Structure

```
futbolche/
├── src/
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── chatbot.py      # NLU: parse_input()
│   │   ├── nlu.py          # Pattern matching engine
│   │   ├── router.py       # Intent routing
│   │   └── intents.json    # Intent definitions & patterns
│   ├── services/
│   │   ├── __init__.py
│   │   ├── clubs_service.py
│   │   ├── players_service.py
│   │   ├── matches_service.py
│   │   ├── leagues_service.py
│   │   ├── statistics_service.py
│   │   └── transfers_service.py
│   ├── db.py               # Database connection & queries
│   ├── main.py             # CLI entry point
│   └── utils/
│       ├── __init__.py
│       └── logger.py       # Command logging
├── sql/
│   ├── schema.sql          # Database schema
│   └── test_data.sql       # Sample data
├── tests/
│   ├── test_*.py           # Unit & integration tests
│   └── test_config.py      # Test database setup
├── docs/
│   ├── COMMANDS.md
│   ├── README.md
│   ├── Example_Scenarios.md
│   └── COMPREHENSIVE_TEST_REPORT.md
├── tools/
├── requirements.txt
└── README.md (root)
```

### Data Flow

1. **Input:** User types command in Bulgarian
2. **NLU Layer** (`chatbot.py`): Parses input, matches against patterns in `intents.json`, extracts parameters, returns intent tag and params dict
3. **Router** (`router.py`): Receives intent + params, validates required parameters, calls appropriate service function
4. **Services** (`services/*.py`): Business logic, database operations, validation
5. **Database** (`db.py`): Low-level SQL execution, connection management
6. **Response:** Service returns result string → Router passes through → Printed to user

### Database Schema

**Tables:**
- `clubs` (id, name, city, founded_year)
- `players` (id, club_id, full_name, birth_date, nationality, position, number, status)
- `matches` (id, home_team_id, away_team_id, match_date, home_goals, away_goals, league_id)
- `leagues` (id, name, season)
- `events` (id, match_id, player_id, event_type, minute)
- `league_teams` (league_id, club_id) - junction table

**Constraints:**
- Foreign keys with ON DELETE CASCADE (players → clubs)
- Unique: club name, player+club combination
- Indexes on foreign keys

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

4. **(Optional) Load sample data:**
   ```bash
   python -c "from db import execute_sql_file; execute_sql_file('sql/test_data.sql')"
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

### Example Session

```
>> помощь
Налични команди:
- помощ
- изход
- добави клуб [club_name]
...

>> създай лига Първа Лига сезон 2025
Лигата 'Първа Лига' (2025) беше създадена успешно.

>> добави клуб Левски
Клубът 'Левски' беше добавен успешно.

>> добави клуб ЦСКА
Клубът 'ЦСКА' беше добавен успешно.

>> добави клуб Левски в лига Първа Лига
Клубът беше добавен в лигата успешно.

>> генерирай кръгове за лига Първа Лига
Календарът беше генериран.

>> изход
До скоро!
```

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
- **Positions**: `GK`, `DF`, `MF`, `FW`
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

If a command fails, review the error message and adjust your input accordingly.

---

## Testing

### Test Suite

The project includes comprehensive tests:

- **Unit Tests** (45 tests): Service layer functions, database operations
- **Integration Tests** (78 tests): End-to-end workflows, NLU pattern matching
- **Total:** 123 tests covering all 21 intents

### Running Tests

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run only integration tests
python -m unittest tests.test_integration_all_intents -v

# Run NLU pattern validation
python tests/test_nlu_patterns.py

# Run specific test module
python -m unittest tests.test_clubs_service -v
```

### Test Reports

See `docs/COMPREHENSIVE_TEST_REPORT.md` for detailed test results, coverage analysis, and known issues.

---

## Maintenance

### Database Maintenance

**Backup:**
```bash
copy sql\futbolche.db sql\futbolche_backup.db
```

**Reset Database:**
```bash
del sql\futbolche.db
python -c "from db import initialize_database; initialize_database()"
```

**Vacuum (optimize):**
```bash
python -c "from db import execute; execute('VACUUM')"
```

### Logging

Command history is logged via `utils/logger.py`. Logs are appended to a file (configure in logger).

To enable/disable logging, modify `log_command()` function.

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

4. Add tests in `tests/` directory.

### Code Style

- Follow PEP 8 guidelines
- Use type hints on function signatures
- Include docstrings for complex functions
- Keep services independent (no direct imports between service modules)

---

## Known Issues

### 1. NLU Pattern Ordering (High Priority)

**Problem:** Sequential first-match-wins pattern matching causes generic patterns to shadow specific ones.

**Affected Intents:**
- `delete_player` shadowed by `delete_club`
- `list_all_players` shadowed by `list_players`
- `add_club_to_league` shadowed by `add_club`
- `record_match` completely broken

**Workarounds:**
- Use numeric IDs for `delete_player`: `"изтрий играч 123"`
- Use `"всички играчи"` for `list_all_players`
- Use `"включи [club] в [league]"` for `add_club_to_league`
- Use alternative `record_match` patterns: `"добави мач ... vs ..."` or `"регистрирай мач ..."`

**Fix:** Reorder `intents.json` to place specific patterns before generic ones, or implement NLU scoring algorithm.

See `docs/COMPREHENSIVE_TEST_REPORT.md` for full analysis.

### 2. `record_match` Pattern Not Matching

The primary pattern `"запиши мач [home] срещу [away] дата [date] резултат [hg]-[ag]"` returns `unknown` intent due to regex construction issues with hyphens. The `_pattern_to_regex()` function in `src/chatbot/nlu.py` needs debugging.

### 3. `record_event` Parameter Extraction

The `event_type` parameter may not be properly extracted from NLU. The router expects it in params, but the pattern may not capture it. The command appears to work, suggesting the router infers event_type from the pattern tag. This needs verification and proper parameter extraction.

### 4. Encoding Issues

Bulgarian text in error messages may display incorrectly in Windows console (code page mismatch). This is cosmetic and doesn't affect functionality. Tests use encoding-agnostic comparisons to mitigate.

---

## Future Enhancements

### Short-term
- [ ] Fix NLU pattern ordering issues
- [ ] Debug and fix `record_match` pattern
- [ ] Implement proper `event_type` extraction in `record_event`
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

## Contributing

This is a learning project. Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

**Guidelines:**
- Write tests for new functionality
- Follow existing code style
- Update documentation
- Ensure all tests pass

---

## License

[Specify license here - e.g., MIT, GPL, etc.]

---

## Contact

For questions, issues, or feedback, please open an issue on the project repository.

---

**Project Version:** 1.0  
**Last Updated:** 2025-03-02  
**Maintainer:** Roo (AI Software Engineer)
