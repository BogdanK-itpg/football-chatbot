# Football League Chatbot

Desktop football management chatbot built with Python and SQLite.

The current app is a Tkinter GUI with:

- Bulgarian natural-language commands
- club, player, league, match, event, transfer, and statistics workflows
- a visual command builder that mirrors the chatbot intents
- a seeded demo database for presentations

The project workspace lives under `futbolche/`.

---

## What It Does

You can use the project to manage a small football ecosystem:

- create and manage clubs
- register and update players
- create leagues and add clubs to them
- generate round-robin schedules
- record matches and match events
- view league tables and fixtures
- view club statistics and player metrics
- transfer players between clubs
- run simple AI-based match predictions

The application ships with a demo-ready preset database so it is usable immediately after startup.

---

## Tech Stack

- Python 3
- SQLite
- Tkinter
- unittest + coverage

---

## Project Layout

```text
football-chatbot/
├── README.md
└── futbolche/
    ├── docs/
    │   ├── COMMANDS.md
    │   ├── README.md
    │   └── database.md
    ├── sql/
    │   ├── football.db
    │   ├── migration.sql
    │   ├── schema.sql
    │   └── seed_demo.sql
    ├── src/
    │   ├── GUI/
    │   ├── ai/
    │   ├── chatbot/
    │   ├── commands/
    │   ├── handlers/
    │   ├── repositories/
    │   ├── services/
    │   ├── utils/
    │   ├── db.py
    │   ├── main.py
    │   └── validators.py
    └── tests/
```

---

## How To Run

From the repository root:

```powershell
cd futbolche
python src/main.py
```

If your machine uses `py` instead of `python`:

```powershell
cd futbolche
py src/main.py
```

This launches the GUI application.

---

## First Startup

On first run, the app will:

- create `futbolche/sql/football.db`
- apply the schema from `futbolche/sql/schema.sql`
- seed the demo dataset from `futbolche/sql/seed_demo.sql`

That means you do not need to manually import demo data before using the project.

---

## How To Run Tests

From the repository root:

```powershell
cd futbolche
python -m unittest discover -s tests -p "test_*.py"
```

---

## How To Run Coverage

From the repository root:

```powershell
cd futbolche
python -m coverage run -m unittest discover -s tests -p "test_*.py"
python -m coverage report -m
```

Optional HTML report:

```powershell
cd futbolche
python -m coverage html
```

Then open:

- `futbolche/htmlcov/index.html`

---

## Main Runtime Flow

The app currently works like this:

1. `src/main.py` starts the GUI
2. `src/GUI/main_window.py` builds the desktop UI
3. User input goes through `src/chatbot/nlu.py`
4. `src/chatbot/router.py` dispatches the matched intent
5. Service modules under `src/services/` run business logic
6. Repository modules under `src/repositories/` run SQL queries
7. `src/db.py` manages SQLite access

The command builder uses the same intent definitions from:

- `src/chatbot/intents.json`

So when we talk about commands in this project, that means both:

- chatbot intents
- command builder navigation/forms

---

## Supported Command Areas

The app supports commands for:

- system help / exit
- club management
- player management
- league management
- standings and fixtures
- match creation and event logging
- club and player statistics
- player transfers
- AI prediction

For the full command reference, see:

- `futbolche/docs/COMMANDS.md`

---

## Demo Database

The demo database design is documented in:

- `futbolche/docs/database.md`

That file describes:

- the intended 10-club football environment
- leagues and team composition
- seeded players, match history, transfers, and events
- presentation scenarios for every command

---

## Useful Files

- `futbolche/src/chatbot/intents.json`
  Intent definitions and command phrases

- `futbolche/src/commands/`
  Command builder metadata and UI

- `futbolche/src/db.py`
  Database initialization, migration, and generic DB helpers

- `futbolche/sql/seed_demo.sql`
  Demo seed data used for new databases

- `futbolche/tests/`
  Current rewritten unit-focused test suite

---

## Notes

- The app is GUI-first, not CLI-first.
- The database file is local and file-based.
- The project currently uses seeded data to make the app presentation-ready on startup.

---

## Documentation

Additional docs:

- `futbolche/docs/README.md`
- `futbolche/docs/COMMANDS.md`
- `futbolche/docs/database.md`
