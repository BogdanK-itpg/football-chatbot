# Football Chatbot - Command Reference

Complete documentation for all chatbot commands, including syntax, parameters, and usage examples.

---

## Table of Contents

1. [System Commands](#system-commands)
2. [Club Management](#club-management)
3. [Player Management](#player-management)
4. [Match Management](#match-management)
5. [League Management](#league-management)
6. [Statistics & Metrics](#statistics--metrics)
7. [Transfers](#transfers)
8. [Events & Fixtures](#events--fixtures)

---

## System Commands

### `help`
Display all available commands.

**Syntax:**
```
помощ
help
какво можеш
команди
```

**Parameters:** None

**Examples:**
```
>> помощь
Налични команди:
- помощ
- изход
- добави клуб [club_name]
...
```

**Notes:** Shows all command patterns from the intents configuration.

---

### `exit`
Exit the chatbot application.

**Syntax:**
```
изход
exit
край
довиждане
```

**Parameters:** None

**Examples:**
```
>> изход
До скоро!
```

---

## Club Management

### `add_club`
Create a new football club.

**Syntax:**
```
добави клуб [club_name]
създай клуб [club_name]
нов клуб [club_name]
добави нов клуб [club_name]
```

**Parameters:**
- `club_name` (string, required): Name of the club to create

**Examples:**
```
>> добави клуб Левски
Клубът 'Левски' беше добавен успешно.

>> създай клуб ЦСКА
Клубът 'ЦСКА' беше добавен успешно.
```

**Validation:**
- Club name cannot be empty
- Club names must be unique (case-insensitive check)
- Default city: 'Unknown'
- Default founding year: 1900

**Error Messages:**
- `"Името не може да бъде празно."` - Empty club name
- `"Клуб с това име вече съществува."` - Duplicate club name

---

### `list_clubs`
Display all registered clubs.

**Syntax:**
```
покажи всички клубове
покажи клубове
списък с клубове
```

**Parameters:** None

**Examples:**
```
>> покажи всички клубове
1. Левски
2. ЦСКА
3. Лудогорец
```

**Output:** Numbered list of all clubs in the database.

**Error Messages:**
- `"Няма добавени клубове."` - No clubs exist

---

### `delete_club`
Remove a club and all associated players.

**Syntax:**
```
изтрий клуб [club_name]
изтрий [club_name]
премахни клуб [club_name]
```

**Parameters:**
- `club_name` (string, required): Name or ID of the club to delete

**Examples:**
```
>> изтрий клуб Левски
Клубът беше изтрит.
```

**Behavior:**
- Deletes the club and cascades to delete all players in that club
- Accepts club name (case-insensitive) or numeric ID

**Error Messages:**
- `"Укажете име на клуба. Формат: изтрий клуб [име]"` - Missing parameter
- `"Клубът не беше намерен."` - Club doesn't exist

**⚠️ Known Issue:** Pattern `"изтрий [club_name]"` may conflict with `delete_player` if the input starts with "изтрий играч". Use the explicit form `"изтрий клуб [name]"` for reliability.

---

### `update_club`
Modify a club's name, city, or founding year.

**Syntax:**
```
редактирай клуб [club_name] на [new_name]
промени клуб [club_name] на [new_name]
```

**Parameters:**
- `club_name` (string, required): Current name or ID of the club
- `new_name` (string, required): New name for the club

**Examples:**
```
>> промени клуб Левски на Левски София
Клубът беше успешно обновен.
```

**Behavior:**
- Updates only the club name (city and founding year not yet supported in this command)
- Resolves club by name (case-insensitive) or ID

**Error Messages:**
- `"Недостатъчни параметри. Формат: редактирай клуб [старо име] на [ново име]"` - Missing parameters
- `"Клубът не беше намерен."` - Club doesn't exist
- `"Няма зададени промени."` - No update parameters provided
- `"Невалидна година на основаване."` - Invalid year if updating founding year

---

## Player Management

### `add_player`
Register a new player in a club.

**Syntax:**
```
добави играч [full_name] в клуб [club_identifier] позиция [position] номер [number] националност [nationality] дата на раждане [birth_date] статус [status]
добави играч [full_name] в [club_identifier]
регистрирай играч [full_name]
създай играч [full_name]
```

**Parameters:**
- `full_name` (string, required): Player's full name
- `club_identifier` (string, required): Club name or ID
- `position` (string, optional but recommended): GK, DF, MF, or FW
- `number` (integer, optional but recommended): Jersey number (1-99)
- `nationality` (string, optional but recommended): Player's nationality
- `birth_date` (string, optional but recommended): Date in YYYY-MM-DD format, not in future
- `status` (string, optional but recommended): Player status (e.g., "активен", "контракт", "свободен")

**Examples:**
```
>> добави играч Иван Петров в клуб Левски позиция FW номер 10 националност България дата на раждане 1995-03-15 статус активен
Играчът беше добавен успешно.

>> добави играч Мария Иванова в 1
Играчът беше добавен успешно.
```

**Validation:**
- Full name: non-empty
- Birth date: valid YYYY-MM-DD format, not in future
- Nationality: non-empty
- Position: must be one of GK, DF, MF, FW
- Number: integer between 1 and 99
- Status: non-empty
- Club must exist

**Error Messages:**
- `"Името на играча не може да бъде празно."`
- `"Невaлидна дата на раждане. Използвайте формат YYYY-MM-DD и дата не може да бъде в бъдещето."`
- `"Националността не може да бъде празна."`
- `"Невaлидна позиция. Използвайте една от: GK, DF, MF, FW."`
- `"Невaлиден номер. Номерът трябва да бъде между 1 и 99."`
- `"Статусът не може да бъде празен."`
- `"Клуб с ID {club_id} не съществува."`

**Notes:** The minimal form `"добави играч [name] в [club]"` works but may result in validation errors if required fields are missing.

---

### `list_players`
Display players in a specific club.

**Syntax:**
```
покажи играчи на клуб [club_identifier]
покажи играчи в клуб [club_identifier]
покажи играчи в [club_identifier]
списък с играчи на [club_identifier]
покажи играчи [club_identifier]
```

**Parameters:**
- `club_identifier` (string, optional): Club name or ID. If omitted, shows all players.

**Examples:**
```
>> покажи играчи на клуб Левски
Ето списък с играчи:
1. #10 Иван Петров (FW)
2. #5 Георги Dimitров (DF)
...

>> покажи играчи
Ето списък с всички играчи:
[all players from all clubs]
```

**Output:** Lists players with jersey number, full name, and position.

**Notes:** The pattern `"покажи всички играчи"` is also used by `list_all_players` intent. Due to pattern ordering issues, it may sometimes match `list_players` instead. If you want all players, use `"всички играчи"` as a fallback.

---

### `list_all_players`
Display all players across all clubs (alternative to `list_players` without parameter).

**Syntax:**
```
покажи всички играчи
всички играчи
списък с всички играчи
```

**Parameters:** None

**Examples:**
```
>> всички играчи
Ето списък с всички играчи:
1. #10 Иван Петров (Левски, FW)
2. #7 Петър Георгиев (ЦСКА, MF)
...
```

**⚠️ Known Issue:** Pattern conflicts with `list_players`. The pattern `"покажи всички играчи"` may incorrectly match `list_players` with "всички" interpreted as a club name. Use `"всички играчи"` (without "покажи") for reliable results.

---

### `update_player_position`
Change a player's position.

**Syntax:**
```
смени позиция на [player_identifier] на [new_position]
промени позиция на [player_identifier] на [new_position]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID
- `new_position` (string, required): New position (GK, DF, MF, FW)

**Examples:**
```
>> смени позиция на Иван Петров на MF
Позицията е обновена.
```

**Validation:**
- Position must be one of: GK, DF, MF, FW
- Player must exist

**Error Messages:**
- `"Недостатъчни параметри. Формат: смени позиция на [player_identifier] на [new_position]"`

---

### `update_player_number`
Change a player's jersey number.

**Syntax:**
```
смени номер на [player_identifier] на [new_number]
промени номер на [player_identifier] на [new_number]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID
- `new_number` (integer, required): New jersey number (1-99)

**Examples:**
```
>> промени номер на Иван Петров на 9
Номерът е обновен.
```

**Validation:**
- Number must be between 1 and 99
- Player must exist

**Error Messages:**
- `"Недостатъчни параметри. Формат: смени номер на [player_identifier] на [new_number]"`
- `"Невaлиден номер. Номерът трябва да бъде между 1 и 99."`

---

### `update_player_status`
Change a player's status.

**Syntax:**
```
смени статус на [player_identifier] на [new_status]
промени статус на [player_identifier] на [new_status]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID
- `new_status` (string, required): New status text

**Examples:**
```
>> смени статус на Иван Петров на свободен
Статусът е обновен.
```

**Validation:**
- Status text cannot be empty
- Player must exist

**Error Messages:**
- `"Недостатъчни параметри. Формат: смени статус на [player_identifier] на [new_status]"`
- `"Статусът не може да бъде празен."`

---

### `delete_player`
Remove a player from the database.

**Syntax:**
```
изтрий играч [player_identifier]
премахни играч [player_identifier]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID

**Examples:**
```
>> изтрий играч Иван Петров
Играчът беше изтрит.
```

**Behavior:**
- Deletes the player from the database
- Accepts player name (exact match, case-insensitive) or numeric ID

**Error Messages:**
- `"Укажете играч за изтриване. Формат: изтрий играч [player_identifier]"`
- `"Играчът не беше намерен."` - Player doesn't exist

**⚠️ Known Issue:** Pattern `"изтрий играч [player]"` may be shadowed by `delete_club` pattern `"изтрий [club_name]"` due to order-dependent matching. If you get club deletion instead, use numeric player ID: `"изтрий играч 123"`.

---

## Match Management

### `record_match`
Log a match with teams, date, and final score.

**Syntax:**
```
запиши мач [home_team] срещу [away_team] дата [match_date] резултат [home_goals]-[away_goals]
добави мач [home_team] vs [away_team] на [match_date] резултат [home_goals]-[away_goals]
регистрирай мач [home_team] - [away_team] [home_goals]:[away_goals] на [match_date]
```

**Parameters:**
- `home_team` (string, required): Home team name or ID
- `away_team` (string, required): Away team name or ID
- `match_date` (string, required): Date in YYYY-MM-DD format
- `home_goals` (integer, required): Goals scored by home team
- `away_goals` (integer, required): Goals scored by away team

**Examples:**
```
>> запиши мач Левски срещу ЦСКА дата 2025-03-15 резултат 2-1
Мачът беше записан с ID 1.

>> добави мач Лудогорец vs Ботев на 2025-03-20 резултат 3-0
Мачът беше записан с ID 2.
```

**Validation:**
- Both teams must exist as clubs
- Teams cannot be the same
- Date format: YYYY-MM-DD
- Goals must be non-negative integers

**Error Messages:**
- `"Недостатъчни параметри. Формат: запиши мач [home_team] срещу [away_team] дата [match_date] резултат [home_goals]-[away_goals]"`
- `"Един от клубовете не съществува."`
- `"Двата отбора не могат да бъдат едни и същи."`
- `"Грешка при запис на мача."`

**❌ Critical Issue:** The primary pattern `"запиши мач [home] срещу [away] дата [date] резултат [hg]-[ag]"` is currently **broken** and returns `unknown` intent. The regex construction in `_pattern_to_regex()` has issues with hyphenated patterns. Workaround: Use alternative patterns `"добави мач ... vs ..."` or `"регистрирай мач ..."` which may work correctly.

---

### `show_match`
Display details of a specific match.

**Syntax:**
```
покажи мач [match_id]
информация за мач [match_id]
детайли за мач [match_id]
```

**Parameters:**
- `match_id` (integer, required): Match ID from database

**Examples:**
```
>> покажи мач 1
2025-03-15: Левски 2-1 ЦСКА
```

**Output:** Date, home team, score, away team.

**Error Messages:**
- `"Формат: покажи мач [match_id]"`
- `"Мачът не е намерен."`

---

### `record_event`
Log an in-game event (goal, assist, card, appearance).

**Syntax:**
```
запиши гол [player_identifier] в мач [match_id] минута [minute]
запиши асист [player_identifier] в мач [match_id] минута [minute]
запиши жълт картон [player_identifier] в мач [match_id] минута [minute]
запиши червен картон [player_identifier] в мач [match_id] минута [minute]
запиши поява [player_identifier] в мач [match_id]
```

**Parameters:**
- `event_type` (implicit from pattern): goal, assist, yellow, red, appearance
- `player_identifier` (string, required): Player name or ID
- `match_id` (integer, required): Match ID
- `minute` (integer, required): Minute of event (not needed for 'appearance')

**Examples:**
```
>> запиши гол Иван Петров в мач 1 минута 34
Събитието беше записано.

>> запиши жълт картон Петър Георгиев в мач 1 минута 67
Събитието беше записано.
```

**Event Types:**
- `гол` - Goal (also updates match goals if match has no score yet)
- `асист` - Assist
- `жълт картон` - Yellow card
- `червен картон` - Red card
- `поява` - Appearance (no minute parameter)

**Validation:**
- Player must exist
- Match must exist
- Minute must be valid integer (1-90+)

**Error Messages:**
- `"Недостатъчни параметри. Формат: запиши събитие [event_type] [player_identifier] в мач [match_id] минута [minute]"`

**⚠️ Known Issue:** The router expects `event_type` in params, but NLU may not extract it properly. The command appears to work because the router may infer it from the pattern tag. This needs verification.

---

### `get_fixtures`
Display all matches in a league.

**Syntax:**
```
покажи мачове в лига [league_identifier]
покажи кръгове за лига [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required): League name or ID

**Examples:**
```
>> покажи мачове в лига Първа Лига
Ето мачовете:
1. 2025-03-15: Левски vs ЦСКА
2. 2025-03-20: Лудогорец vs Ботев
...
```

**Output:** List of matches with dates and team pairings.

**Notes:** This is an alias for viewing generated fixtures. Use `generate_round_robin` first to create the schedule.

---

## League Management

### `create_league`
Create a new league/competition.

**Syntax:**
```
създай лига [league_name] сезон [season]
добави лига [league_name] [season]
```

**Parameters:**
- `league_name` (string, required): Name of the league
- `season` (string, required): Season identifier (e.g., "2024-2025", "2025")

**Examples:**
```
>> създай лига Първа Лига сезон 2025
Лигата 'Първа Лига' (2025) беше създадена успешно.

>> добави лига Втора Лига 2024-2025
Лигата 'Втора Лига' (2024-2025) беше създадена успешно.
```

**Validation:**
- League name cannot be empty
- Season cannot be empty

**Error Messages:**
- `"Името на лигата не може да бъде празно."`

---

### `add_club_to_league`
Add a club to a league's roster.

**Syntax:**
```
добави клуб [club_identifier] в лига [league_identifier]
включи [club_identifier] в [league_identifier]
```

**Parameters:**
- `club_identifier` (string, required): Club name or ID
- `league_identifier` (string, required): League name or ID

**Examples:**
```
>> добави клуб Левски в лига Първа Лига
Клубът беше добавен в лигата успешно.

>> включи ЦСКА в Първа Лига
Клубът беше добавен в лигата успешно.
```

**Validation:**
- Club must exist
- League must exist
- Club cannot be added twice to same league

**Error Messages:**
- `"Лигата не съществува."`
- `"Клубът не съществува."`
- `"Грешка при добавяне на клуба в лигата (възможно дублиране)."`

**⚠️ Known Issue:** Pattern `"добави клуб [club] в лига [league]"` may be shadowed by `add_club` pattern `"добави клуб [club_name]"` due to order-dependent matching. Use alternative pattern `"включи [club] в [league]"` for reliable results.

---

### `get_league_teams`
List all clubs participating in a league.

**Syntax:**
```
покажи отбори в лига [league_identifier]
покажи отборите на [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required): League name or ID

**Examples:**
```
>> покажи отбори в лига Първа Лига
Ето отборите в лигата:
1. Левски
2. ЦСКА
3. Лудогорец
```

**Output:** List of clubs in the league.

**Error Messages:**
- `"Лигата не съществува."` (returns empty list if not found)

---

### `generate_round_robin`
Automatically generate match fixtures for a league using round-robin scheduling.

**Syntax:**
```
генерирай кръгове за лига [league_identifier]
създай кръгове [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required): League name or ID

**Optional Parameters (via function signature, not exposed in patterns):**
- `double_round` (boolean): Generate home-and-away fixtures (default: False, single round-robin)
- `start_date` (string, YYYY-MM-DD): First match day (default: today)
- `interval_days` (integer): Days between match rounds (default: 7)

**Examples:**
```
>> генерирай кръгове за лига Първа Лига
Календарът беше генериран.
```

**Behavior:**
- Requires at least 2 teams in the league
- Generates all pairwise matchups
- For odd number of teams, uses bye weeks
- Creates match records with home/away assignments
- Schedules matches at weekly intervals starting from today (or specified start_date)

**Error Messages:**
- `"Недостатъчно отбори за създаване на кръгове."` - Less than 2 teams
- `"Лигата не съществува."`

**Notes:** This creates unplayed match fixtures (scores are NULL). Use `record_match` to update results, or `record_event` to log in-game events.

---

### `get_standings`
Display the league table with computed rankings.

**Syntax:**
```
покажи класиране [league_identifier]
класиране на лига [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required): League name or ID

**Examples:**
```
>> покажи класиране Първа Лига
Ето класирането:
1. Левски    P:6 W:4 D:1 L:1 GF:12 GA:5 GD:+7 Pts:13
2. ЦСКА      P:6 W:3 D:2 L:1 GF:9 GA:4 GD:+5 Pts:11
3. Лудогорец P:6 W:2 D:1 L:3 GF:7 GA:10 GD:-3 Pts:7
...
```

**Columns:**
- P: Played matches
- W: Wins
- D: Draws
- L: Losses
- GF: Goals For
- GA: Goals Against
- GD: Goal Difference
- Pts: Points (3 for win, 1 for draw)

**Sorting:** Primary: Points (descending), Secondary: Goal Difference, Tertiary: Goals For

**Error Messages:**
- `"Формат: покажи класиране [league_identifier]"`

**Notes:** Only counts matches with both teams' scores recorded (played matches).

---

## Statistics & Metrics

### `club_statistics`
Display detailed statistics for a club.

**Syntax:**
```
покажи статистика на клуб [club_identifier]
статистика на клуб [club_identifier]
класиране на [club_identifier]
къде е клуб [club_identifier]
```

**Parameters:**
- `club_identifier` (string, required): Club name or ID

**Examples:**
```
>> покажи статистика на клуб Левски
Статистика за клуб Левски:
Игри: 6, Победи: 4, Равни: 1, Загуби: 1,
Голове за: 12, Голове срещу: 5, Голова разлика: 7, Точки: 13
```

**Output Metrics:**
- Played matches
- Wins, Draws, Losses
- Goals For (GF)
- Goals Against (GA)
- Goal Difference (GD)
- Points (Pts)

**Error Messages:**
- `"Недостатъчни параметри. Формат: покажи статистика на клуб [club_identifier]"`
- `"Клуб '...' не съществува."`

---

### `player_statistics`
Display basic statistics for a player.

**Syntax:**
```
покажи статистика на играч [player_identifier]
статистика на играч [player_identifier]
покажи статистика [player_identifier]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID

**Examples:**
```
>> покажи статистика на играч Иван Петров
Статистика за играч Иван Петров:
Голове: 5, Асистенции: 2,
Появи: 15, Жълти: 2, Червени: 0
```

**Output Metrics:**
- Goals
- Assists
- Appearances (matches played)
- Yellow cards
- Red cards

**Error Messages:**
- `"Недостатъчни параметри. Формат: покажи статистика на играч [player_identifier]"`
- `"Играч '...' не съществува."`

---

### `player_metrics`
Display advanced per-90 minute metrics for a player.

**Syntax:**
```
покажи метрики на играч [player_identifier]
покажи разширени метрики на играч [player_identifier]
метрики на играч [player_identifier]
покажи показатели на играч [player_identifier]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID

**Examples:**
```
>> покажи метрики на играч Иван Петров
Разширени метрики за Иван Петров:
Мин. (прибл.): 1350, Гол/90: 0.33, Асист/90: 0.13
```

**Output Metrics:**
- Minutes played (approximated as appearances × 90)
- Goals per 90 minutes
- Assists per 90 minutes

**Calculation:**
- `minutes_played = appearances × 90`
- `goals_per_90 = (goals / appearances) × 90` (if appearances > 0)
- `assists_per_90 = (assists / appearances) × 90` (if appearances > 0)

**Error Messages:**
- `"Недостатъчни параметри. Формат: покажи метрики на играч [player_identifier]"`
- `"Играч '...' не съществува."`

**Notes:** These are approximate metrics since actual minutes played are not tracked. For more accurate metrics, consider tracking minutes in the events table.

---

## Transfers

### `transfer_player`
Move a player from one club to another.

**Syntax:**
```
трансферирай играч [player_identifier] в клуб [club_identifier]
прехвърли играч [player_identifier] в [club_identifier]
трансфер [player_identifier] -> [club_identifier]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID
- `club_identifier` (string, required): Destination club name or ID

**Examples:**
```
>> трансферирай играч Иван Петров в клуб ЦСКА
Играчът беше трансфериран.

>> трансфер Петър Георгиев -> Лудогорец
Играчът беше трансфериран.
```

**Behavior:**
- Executes within a database transaction (atomic operation)
- Updates player's club_id
- Handles jersey number conflicts: if the destination club already has the same number, assigns the smallest available number (1-99)
- Prevents transferring to the same club
- Logs the transfer in command history

**Special Cases:**
- If jersey number is taken in destination club, automatically reassigns to first available number
- Transfer to same club returns: `"Играчът вече е в този клуб."`

**Error Messages:**
- `"Играч '...' не съществува."`
- `"Клуб '...' не съществува."`
- `"Грешка при трансфер на играча."`

**Response Examples:**
```
Играч 'Иван Петров' беше трансфериран в клуб с ID 2.
Играч 'Петър Георгиев' беше трансфериран в клуб с ID 3. Присвоен нов номер: #11.
```

---

## Events & Fixtures

### `get_fixtures` (alias)
Display all matches in a league.

See [Match Management](#match-management) section for full documentation.

---

## Parameter Reference

### Identifier Resolution

Many commands accept `club_identifier` or `player_identifier` parameters. The system resolves these using:

1. **Exact match** (case-insensitive): "Левски" matches club name "Левски"
2. **Numeric ID**: Integer values match database ID directly
3. **Fuzzy match** (contains): "Лев" matches "Левски" if no exact match

**Examples:**
```
>> покажи играчи на клуб 1        # Uses club ID
>> покажи играчи на клуб Левски   # Exact name match
>> покажи играчи на клуб Лев      # Contains match (finds Левски)
```

### Date Format

All dates use ISO 8601 format: `YYYY-MM-DD`

**Examples:**
- `2025-03-15`
- `2024-12-31`
- `2025-01-01`

**Validation:** Must be a valid calendar date and not in the future (for birth dates).

### Position Codes

Player positions use 2-letter codes:
- `GK` - Goalkeeper
- `DF` - Defender
- `MF` - Midfielder
- `FW` - Forward

---

## Known Issues & Limitations

### 1. NLU Pattern Ordering

The chatbot uses first-match-wins sequential pattern matching. This causes 4 intents to have pattern conflicts:

**Affected Commands:**
- `delete_player` vs `delete_club`
- `list_all_players` vs `list_players`
- `add_club_to_league` vs `add_club`
- `record_match` (completely broken)

**Workarounds:**
- For `delete_player`: Use numeric player ID: `"изтрий играч 123"`
- For `list_all_players`: Use `"всички играчи"` instead of `"покажи всички играчи"`
- For `add_club_to_league`: Use `"включи [club] в [league]"` pattern
- For `record_match`: Use alternative patterns `"добави мач ... vs ..."` or `"регистрирай мач ..."`

**Recommended Fix:** Reorder intents in `intents.json` to place specific patterns before generic ones.

### 2. `record_match` Broken

The primary pattern `"запиши мач [home] срещу [away] дата [date] резултат [hg]-[ag]"` returns `unknown` intent due to regex construction issues with hyphens. Use alternative patterns until fixed.

### 3. `record_event` Parameter Extraction

The `event_type` parameter may not be properly extracted from NLU, though the command appears to work. The router might be inferring it from the pattern tag. This needs verification.

### 4. Encoding Issues

Bulgarian error messages may display incorrectly in Windows console (cp1252 vs cp1251). This affects test output but not actual functionality.

---

## Command Quick Reference

| Command | Purpose | Key Parameters |
|---------|---------|----------------|
| `помощ` | Show all commands | - |
| `изход` | Exit chatbot | - |
| `добави клуб` | Create club | club_name |
| `покажи клубове` | List all clubs | - |
| `изтрий клуб` | Delete club | club_name |
| `редактирай клуб` | Update club | club_name, new_name |
| `добави играч` | Add player | full_name, club, position, number, nationality, birth_date, status |
| `покажи играчи` | List players | club_identifier (optional) |
| `изтрий играч` | Delete player | player_identifier |
| `смени позиция` | Update player position | player_identifier, new_position |
| `смени номер` | Update player number | player_identifier, new_number |
| `смени статус` | Update player status | player_identifier, new_status |
| `покажи статистика` | Club stats | club_identifier |
| `покажи статистика на играч` | Player stats | player_identifier |
| `покажи метрики` | Player advanced metrics | player_identifier |
| `трансферирай играч` | Transfer player | player_identifier, to_club |
| `запиши мач` | Record match | home_team, away_team, date, home_goals, away_goals |
| `покажи мач` | Show match details | match_id |
| `запиши събитие` | Log in-game event | player_identifier, match_id, event_type, minute |
| `създай лига` | Create league | league_name, season |
| `добави клуб в лига` | Add club to league | club_identifier, league_identifier |
| `покажи отбори в лига` | List league teams | league_identifier |
| `генерирай кръгове` | Generate fixtures | league_identifier |
| `покажи класиране` | Show league standings | league_identifier |

---

**Document Version:** 1.0  
**Last Updated:** 2025-03-02  
**Based on:** `intents.json` and service layer implementation
