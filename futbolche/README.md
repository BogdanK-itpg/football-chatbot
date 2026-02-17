# Football League Chatbot

A Python-based chatbot for managing football clubs using SQLite database.

## Features

- **CRUD Operations**: Add, view, and delete football clubs
- **Natural Language Interface**: Chat with the bot using Bulgarian commands
- **Persistent Storage**: SQLite database for data persistence
- **Command Logging**: All commands are logged for audit trail

## Project Structure

```
futbolche/
├── src/
│   ├── main.py          # Main chat loop
│   ├── db.py            # Database connection and query execution
│   ├── chatbot.py       # Intent parsing and handling
│   ├── intents.json     # Intent definitions and patterns
│   └── clubs_service.py # CRUD operations for clubs
├── sql/
│   ├── schema.sql       # Database schema
│   └── football.db      # SQLite database (auto-created)
├── commands.log         # Command history log
├── test_setup.py        # Test script for verification
└── README.md
```

## Requirements

- Python 3.8+
- SQLite3 (included in Python standard library)

## Installation

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd futbolche
   ```
3. The database will be created automatically on first run

## Usage

Run the chatbot:

```bash
cd futbolche/src
python main.py
```

Or from the project root:

```bash
python src/main.py
```

## Available Commands

- **Добави клуб <име>** - Add a new club
- **Покажи всички клубове** - List all clubs
- **Изтрий клуб <име>** - Delete a club
- **помощ** - Show help message
- **изход** - Exit the chatbot

## Examples

```
>> Добави клуб Левски София
Клуб 'Левски София' беше добавен успешно.

>> Покажи всички клубове
1. Левски София

>> Изтрий клуб Левски София
Клуб 'Левски София' беше изтрит.

>> помощ
Налични команди:
- Добави клуб <име>
- Покажи всички клубове
- Изтрий клуб <име>
- помощ
- изход

>> изход
До скоро!
```

## Database Schema

The database consists of three tables:

- **clubs**: Stores football club information (id, name, city, founded_year)
- **players**: Stores player information linked to clubs
- **matches**: Stores match data with home/away teams

## Testing

Run the test script to verify database initialization and CRUD operations:

```bash
python test_setup.py
```

## Logging

All commands and their results are logged to `commands.log` with timestamps.

## GitHub Deployment

This project is ready for GitHub. Key files included:
- Complete source code in `src/`
- Database schema in `sql/schema.sql`
- Comprehensive README
- Test script
- Command logging

## License

Educational project - Free to use and modify.
