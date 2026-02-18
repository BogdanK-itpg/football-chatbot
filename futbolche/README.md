# Football League Chatbot

A Python-based conversational AI chatbot for managing football league data through natural language commands. Built with SQLite for persistent storage and featuring full CRUD operations for both football clubs and players.

## Features

### Core Capabilities
- **Natural Language Interface**: Interact using Bulgarian conversational commands
- **Club Management**: Full CRUD operations (Create, Read, Delete) for football clubs
- **Player Management**: Complete CRUD operations for players including position, number, and status updates
- **Smart Intent Recognition**: Pattern-based parsing with flexible command variations
- **Persistent Storage**: SQLite database with foreign key constraints and cascade deletes
- **Command Logging**: All interactions logged with timestamps for audit trail
- **Sample Data**: Auto-initialization with 8 clubs and 38 players for testing

### Technical Features
- **Modular Architecture**: Separated concerns with service layers
- **Input Validation**: Comprehensive validation for dates, positions, jersey numbers
- **Case-Insensitive Search**: Find clubs and players by name or ID
- **Error Handling**: Graceful error messages for invalid inputs
- **Regex Pattern Matching**: Flexible command parsing from JSON-defined intents

## Project Structure

```
futbolche/
├── src/
│   ├── main.py          # Main chat loop and command logging
│   ├── db.py            # Database connection, initialization, and query execution
│   ├── chatbot.py       # Intent parsing, pattern matching, and command routing
│   ├── intents.json     # Declarative intent definitions and response templates
│   ├── clubs_service.py # Club management business logic
│   └── players_service.py # Player management business logic
├── sql/
│   ├── schema.sql       # Database schema with constraints
│   └── football.db      # SQLite database (auto-created on first run)
├── commands.log         # Command history and interaction log
├── test_setup.py        # Test script for database verification and sample data
├── SAMPLE_DIALOG.md     # Example conversation demonstrating all features
└── README.md
```

## Requirements

- **Python**: 3.8 or higher
- **Dependencies**: None (uses only Python standard library)
  - `sqlite3` - Database (included)
  - `json`, `re`, `os`, `datetime` - All standard library

## Installation & Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd futbolche
   ```

2. **Initialize the database** (automatic on first run)
   - The database is created automatically when you first run the chatbot
   - Sample data (8 clubs, 38 players) is inserted on initial creation
   - Database file: `sql/football.db`

3. **Verify installation** (optional)
   ```bash
   python test_setup.py
   ```
   This will clear and recreate test data, showing you the database is working.

## Usage

### Starting the Chatbot

From the project root:
```bash
python src/main.py
```

Or navigate to the src directory:
```bash
cd src
python main.py
```

### Interaction

The chatbot prompts with `>>`. Type your commands in Bulgarian. Type `помощ` or `exit` to see commands or quit.

## Available Commands

### Club Management
- **Добави клуб <име>** - Add a new club (city defaults to "Unknown", year to 1900)
  - Examples: `добави клуб Левски София`, `създай клуб ЦСКА`, `нов клуб Ботев`
  
- **Покажи всички клубове** - List all clubs with IDs
  - Output: `1. Левски София`, `2. ЦСКА София`, etc.
  
- **Изтрий клуб <име>** - Delete a club (cascades to players)
  - Examples: `изтрий клуб Левски`, `махни клуб Ботев`

- **Редактирай клуб <име>** - (Not yet implemented)

### Player Management
- **Добави играч [full_name] в клуб [club_identifier] позиция [position] номер [number] националност [nationality] дата на раждане [birth_date] статус [status]**
  - Add a new player to a club
  - `position`: GK, DF, MF, FW
  - `number`: 1-99
  - `birth_date`: YYYY-MM-DD format, not in future
  - `club_identifier`: club name or ID
  - Example: `добави играч Иван Иванов в клуб Левски София позиция GK номер 1 националност България дата на раждане 1995-03-15 статус Активен`

- **Покажи играчи на клуб [club_identifier]** - List players for a specific club
  - Example: `покажи играчи на клуб Левски София`
  
- **Покажи всички играчи** - List all players across all clubs (ordered by club, then number)

- **Смени номер на [player_identifier] на [new_number]** - Update player's jersey number
  - `player_identifier`: player name or ID
  - Example: `смени номер на Иван Иванов на 99`

- **Смени позиция на [player_identifier] на [new_position]** - Update player's position
  - Example: `смени позиция на Петър Петров на MF`

- **Смени статус на [player_identifier] на [new_status]** - Update player's status
  - Example: `смени статус на Иван Иванов на Контузиран`

- **Изтрий играч [player_identifier]** - Delete a player
  - Example: `изтрий играч Иван Иванов` or `изтрий играч 1`

### System Commands
- **помощ** or **help** - Show all available commands
- **изход** or **exit** or **quit** - Exit the chatbot

## Command Examples

```
>> помощ
Налични команди:
- добави клуб <име>
- покажи всички клубове
- изтрий клуб <име>
- помощ
- изход
- добави играч [full_name] в клуб [club_identifier] позиция [position] номер [number] националност [nationality] дата на раждане [birth_date] статус [status]
- покажи играчи на клуб [club_identifier]
- смени номер на [player_identifier] на [new_number]
- смени позиция на [player_identifier] на [new_position]
- смени статус на [player_identifier] на [new_status]
- изтрий играч [player_identifier]

>> добави клуб Левски София
Клуб 'Левски София' беше добавен успешно.

>> покажи всички клубове
1. Левски София

>> добави играч Иван Иванов в клуб Левски София позиция GK номер 1 националност България дата на раждане 1995-03-15 статус Активен
Играч 'Иван Иванов' беше добавен успешно.

>> покажи играчи на клуб Левски София
ID: 1 | Иван Иванов | Левски София | GK | #1 | България | 1995-03-15 | Активен

>> смени номер на Иван Иванов на 99
Номерът на играч с ID 1 беше сменен на 99.

>> изтрий играч 1
Играч с ID 1 беше изтрит.

>> изход
До скоро!
```

## Database Schema

### Tables

#### `clubs`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| name | TEXT | Club name (unique, not null) |
| city | TEXT | City where club is based |
| founded_year | INTEGER | Year of establishment |

#### `players`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| club_id | INTEGER | Foreign key to clubs.id (cascade delete) |
| full_name | TEXT | Player's full name |
| birth_date | TEXT | Birth date in YYYY-MM-DD format |
| nationality | TEXT | Player's nationality |
| position | TEXT | Position: GK, DF, MF, FW |
| number | INTEGER | Jersey number (1-99) |
| status | TEXT | Current status (e.g., "Активен", "Контузиран") |

#### `matches` (schema only, not implemented)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| home_team_id | INTEGER | Foreign key to clubs.id |
| away_team_id | INTEGER | Foreign key to clubs.id |
| home_goals | INTEGER | Goals scored by home team |
| away_goals | INTEGER | Goals scored by away team |
| match_date | TEXT | Date of the match |

**Foreign Keys**: `PRAGMA foreign_keys = ON` ensures referential integrity.

## Sample Data

On first initialization, the database is populated with:

**Clubs (8 total):**
- Левски София (София, 1914)
- ЦСКА София (София, 1948)
- Ботев Пловдив (Пловдив, 1912)
- Лудогорец Разград (Разград, 1945)
- Черно море Варна (Варна, 1913)
- Спартак Варна (Варна, 1929)
- Локомотив Пловдив (Пловдив, 1926)
- Берое Стара Загора (Стара Загора, 1916)

**Players (38 total):** 5 players per club with realistic Bulgarian names, positions, and valid data.

## Testing

The `test_setup.py` script provides comprehensive testing:

```bash
python test_setup.py
```

**What it does:**
- Initializes the database
- Clears all existing data
- Creates 5 test clubs
- Creates 12 test players distributed across clubs
- Shows summary statistics
- Provides next steps

**Expected output:**
```
============================================================
FOOTBALL CHATBOT - TEST SETUP
============================================================
[TEST SETUP] Database initialized
[TEST SETUP] Cleared existing data
[TEST SETUP] Creating test clubs...
[TEST SETUP] Created club: Левски София (ID: 1)
...
[TEST SETUP] Created 5 clubs
[TEST SETUP] Creating test players...
[TEST SETUP] Created player: Иван Иванов (GK, #1) at club ID 1
...
============================================================
TEST SETUP COMPLETE
============================================================
Total clubs: 5
Total players: 12

You can now run the chatbot with: python src/main.py
```

## Logging

All commands and responses are logged to `commands.log` in CSV-like format:
```
2026-02-17 21:05:36.861053 | помощ | Налични команди:...
```

Use this for:
- Debugging user interactions
- Auditing command history
- Analyzing usage patterns

## Architecture Highlights

### Intent System
- Intents defined declaratively in `intents.json`
- Patterns use placeholders `[parameter]` for dynamic values
- Automatic regex generation with flexible whitespace matching
- Case-insensitive matching

### Service Layer
- `clubs_service.py`: Club CRUD operations
- `players_service.py`: Player CRUD with validation
- `db.py`: Database abstraction with connection pooling

### Validation
- **Positions**: Must be GK, DF, MF, or FW
- **Jersey Numbers**: 1-99 range check
- **Birth Dates**: YYYY-MM-DD format, not in future
- **Duplicate Checks**: Club names unique, player names unique per club
- **Foreign Keys**: Club must exist before adding players

## Development Notes

### Current Limitations
- Club update/edit functionality not implemented (returns "not implemented" message)
- Matches table exists but no CRUD operations for matches
- No user authentication or authorization
- Single-language (Bulgarian) interface only

### Extension Points
- Add match scheduling and results
- Implement club editing (city, founded_year)
- Add league standings calculations
- Implement player search and filtering
- Add data export (JSON, CSV)
- Web interface using Flask/FastAPI

## GitHub Deployment

This project is GitHub-ready with:
- ✅ Complete source code in `src/`
- ✅ Database schema in `sql/schema.sql`
- ✅ Comprehensive documentation (this README)
- ✅ Sample dialog in `SAMPLE_DIALOG.md`
- ✅ Test script for verification
- ✅ Command logging for debugging
- ✅ .gitignore for Python projects

### Recommended .gitignore
```
__pycache__/
*.pyc
sql/football.db
commands.log
.vscode/
.idea/
*.egg-info/
dist/
build/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly: `python test_setup.py`
4. Commit with clear messages: `git commit -m "Add feature X"`
5. Push to your fork: `git push origin feature-name`
6. Open a Pull Request with description

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names (Bulgarian or English)
- Add docstrings to functions
- Keep functions single-purpose
- Validate all user inputs

## License

Educational project - Free to use, modify, and distribute.

## Author

Created as a football league management system with natural language interface.

---

**Need help?** Run the chatbot and type `помощ` to see all available commands.
