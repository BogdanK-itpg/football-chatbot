# Football Chatbot - Command Reference

Complete reference for every current command intent in `src/chatbot/intents.json`.

This document is intentionally aligned with the current app behavior:

- chatbot intents
- router behavior
- command builder coverage

---

## Table of Contents

1. [System Commands](#system-commands)
2. [Club Management](#club-management)
3. [Player Management](#player-management)
4. [Match Management](#match-management)
5. [League Management](#league-management)
6. [Statistics & Metrics](#statistics--metrics)
7. [Transfers](#transfers)
8. [Prediction](#prediction)
9. [Parameter Reference](#parameter-reference)

---

## System Commands

### `help`
Display all available commands.

**Syntax:**
```text
помощ
help
какво можеш
команди
```

**Parameters:** None

**Example:**
```text
>> помощ
Налични команди:
...
```

---

### `exit`
Exit the chatbot.

**Syntax:**
```text
изход
exit
край
довиждане
```

**Parameters:** None

**Example:**
```text
>> изход
До скоро!
```

---

## Club Management

### `add_club`
Create a new club.

**Syntax:**
```text
добави клуб [club_name]
създай клуб [club_name]
нов клуб [club_name]
добави нов клуб [club_name]
```

**Parameters:**
- `club_name` (string, required): Club name

**Example:**
```text
>> добави клуб Дунав Русе
Клуб 'Дунав Русе' беше добавен успешно.
```

**Error Messages:**
- `Името не може да бъде празно.`
- `Клуб с това име вече съществува.`

---

### `list_clubs`
List all clubs.

**Syntax:**
```text
покажи всички клубове
покажи клубове
списък с клубове
```

**Parameters:** None

**Example:**
```text
>> покажи клубове
1. Левски София
2. ЦСКА София
...
```

---

### `delete_club`
Delete a club.

**Syntax:**
```text
изтрий клуб [club_name]
премахни клуб [club_name]
```

**Parameters:**
- `club_name` (string, required): Club name or ID

**Example:**
```text
>> изтрий клуб Дунав Русе
Клуб 'Дунав Русе' беше изтрит.
```

**Error Messages:**
- `Укажете име на клуба. Формат: изтрий клуб [име]`
- `Няма такъв клуб.`

---

### `update_club`
Rename a club.

**Syntax:**
```text
редактирай клуб [club_name] на [new_name]
промени клуб [club_name] на [new_name]
```

**Parameters:**
- `club_name` (string, required): Current club name or ID
- `new_name` (string, required): New club name

**Example:**
```text
>> промени клуб Ботев Враца на Ботев Враца 1921
Клубът беше успешно обновен.
```

**Error Messages:**
- `Невалидни параметри.`
- `Формат: редактирай клуб [старо име] на [ново име]`
- `Клубът не беше намерен.`

---

## Player Management

### `add_player`
Create a player.

**Syntax:**
```text
добави играч [full_name] в клуб [club_identifier] позиция [position] номер [number] националност [nationality] дата на раждане [birth_date] статус [status]
добави играч [full_name] в [club_identifier]
регистрирай играч [full_name]
създай играч [full_name]
```

**Parameters:**
- `full_name` (string, required): Full player name
- `club_identifier` (string, required for working creation flow): Club name or ID
- `position` (string, required in full form): `GK`, `DF`, `MF`, `FW`
- `number` (integer, required in full form): Shirt number
- `nationality` (string, required in full form)
- `birth_date` (string, required in full form): `YYYY-MM-DD`
- `status` (string, required in full form)

**Example:**
```text
>> добави играч Николай Георгиев в клуб Левски София позиция FW номер 19 националност България дата на раждане 2001-04-17 статус Активен
Играч 'Николай Георгиев' беше добавен успешно.
```

**Error Messages:**
- `Името на играча не може да бъде празно.`
- `Невaлидна дата на раждане. Използвайте формат YYYY-MM-DD и дата не може да бъде в бъдещето.`
- `Националността не може да бъде празна.`
- `Невaлидна позиция. Използвайте една от: GK, DF, MF, FW.`
- `Невaлиден номер. Номерът трябва да бъде между 1 и 99.`
- `Статусът не може да бъде празен.`

---

### `list_players`
List players from a club.

**Syntax:**
```text
покажи играчи на клуб [club_identifier]
покажи играчи в клуб [club_identifier]
покажи играчи в [club_identifier]
списък с играчи на [club_identifier]
покажи играчи [club_identifier]
```

**Parameters:**
- `club_identifier` (string, required): Club name or ID

**Example:**
```text
>> покажи играчи на клуб Левски София
ID  Име                   Клуб                    Поз  №   Националност   Р. Дата     Статус
...
```

---

### `list_all_players`
List all players.

**Syntax:**
```text
покажи всички играчи
всички играчи
списък с всички играчи
```

**Parameters:** None

**Example:**
```text
>> покажи всички играчи
ID  Име                   Клуб                    Поз  №   Националност   Р. Дата     Статус
...
```

---

### `update_player_position`
Update a player's position.

**Syntax:**
```text
смени позиция на [player_identifier] на [new_position]
промени позиция на [player_identifier] на [new_position]
```

**Parameters:**
- `player_identifier` (string, required)
- `new_position` (string, required): `GK`, `DF`, `MF`, `FW`

**Example:**
```text
>> смени позиция на Александър Колев на MF
Позицията на играч с ID 5 беше обновена на MF.
```

---

### `update_player_number`
Update a player's shirt number.

**Syntax:**
```text
смени номер на [player_identifier] на [new_number]
промени номер на [player_identifier] на [new_number]
```

**Parameters:**
- `player_identifier` (string, required)
- `new_number` (integer, required)

**Example:**
```text
>> смени номер на Александър Колев на 99
Номерът на играч с ID 5 беше сменен на 99.
```

---

### `update_player_status`
Update a player's status.

**Syntax:**
```text
смени статус на [player_identifier] на [new_status]
промени статус на [player_identifier] на [new_status]
```

**Parameters:**
- `player_identifier` (string, required)
- `new_status` (string, required)

**Example:**
```text
>> смени статус на Александър Колев на Контузен
Статусът на играч с ID 5 беше обновен на 'Контузен'.
```

---

### `delete_player`
Delete a player.

**Syntax:**
```text
изтрий играч [player_identifier]
премахни играч [player_identifier]
```

**Parameters:**
- `player_identifier` (string, required): Player name or ID

**Example:**
```text
>> изтрий играч 50
Играч с ID 50 беше изтрит.
```

---

## Match Management

### `record_match`
Create a played match record.

**Syntax:**
```text
запиши мач [home_team] срещу [away_team] дата [match_date] резултат [home_goals]-[away_goals]
добави мач [home_team] vs [away_team] на [match_date] резултат [home_goals]-[away_goals]
регистрирай мач [home_team] - [away_team] [home_goals]:[away_goals] на [match_date]
запиши мач [home_team] срещу [away_team] дата [match_date] резултат [home_goals]-[away_goals] лига [league] кръг [round_no]
добави мач [home_team] vs [away_team] на [match_date] резултат [home_goals]-[away_goals] лига [league] кръг [round_no]
```

**Parameters:**
- `home_team` (string, required)
- `away_team` (string, required)
- `match_date` (string, required): `YYYY-MM-DD`
- `home_goals` (integer, required)
- `away_goals` (integer, required)
- `league` (string, optional)
- `round_no` (integer, optional)

**Example:**
```text
>> запиши мач Берое Стара Загора срещу Арда Кърджали дата 2025-09-12 резултат 2-1 лига Втора Лига кръг 6
Мачът беше записан с ID 41.
```

---

### `show_match`
Show one match.

**Syntax:**
```text
покажи мач [match_id]
информация за мач [match_id]
детайли за мач [match_id]
```

**Parameters:**
- `match_id` (integer, required)

**Example:**
```text
>> покажи мач 1
2025-08-01: Левски София 2-1 ЦСКА София
```

---

### `record_event`
Record a match event.

**Syntax:**
```text
запиши гол [player_identifier] в мач [match_id] минута [minute]
запиши асист [player_identifier] в мач [match_id] минута [minute]
запиши жълт картон [player_identifier] в мач [match_id] минута [minute]
запиши червен картон [player_identifier] в мач [match_id] минута [minute]
запиши поява [player_identifier] в мач [match_id]
запиши [event_type] [player_identifier] в мач [match_id] минута [minute]
```

**Parameters:**
- `player_identifier` (string, required)
- `match_id` (integer, required)
- `minute` (integer, required except for `поява`)
- `event_type` (implicit or explicit): `goal`, `assist`, `yellow`, `red`, `appearance`

**Example:**
```text
>> запиши гол Александър Колев в мач 21 минута 73
Събитието беше записано успешно.
```

---

### `show_events`
Show all events for a match.

**Syntax:**
```text
покажи събития [match_id]
покажи събития
събития за мач [match_id]
```

**Parameters:**
- `match_id` (integer, required in practice for useful execution)

**Example:**
```text
>> покажи събития 1
23' - ГОЛ - Александър Колев
44' - АСИСТЕНЦИЯ - Георги Миланов
...
```

---

### `show_round`
Show a round from a league.

**Syntax:**
```text
покажи кръг [round_no] [league_name]
```

**Parameters:**
- `round_no` (integer, required)
- `league_name` (string, required)

**Example:**
```text
>> покажи кръг 1 Първа Лига
--- Кръг 1 ---
ID:1 | 2025-08-01 | Левски София 2:1 ЦСКА София | ИЗИГРАН
...
```

---

### `get_fixtures`
Show league fixtures.

**Syntax:**
```text
покажи мачове в лига [league_identifier]
покажи кръгове за лига [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required)

**Example:**
```text
>> покажи мачове в лига Първа Лига
2025-08-01: Левски София vs ЦСКА София (2-1)
...
```

---

## League Management

### `create_league`
Create a new league.

**Syntax:**
```text
създай лига [league_name] за сезон [season]
добави лига [league_name] за сезон [season]
създай лига [league_name] сезон [season]
нова лига [league_name] сезон [season]
създай лига [league_name] [season]
добави лига [league_name] [season]
нова лига [league_name] [season]
```

**Parameters:**
- `league_name` (string, required)
- `season` (string, required)

**Example:**
```text
>> създай лига Купа на България сезон 2025
Лига 'Купа на България' (2025) беше създадена успешно.
```

---

### `add_club_to_league`
Add a club to a league.

**Syntax:**
```text
добави клуб [club_identifier] в лига [league_identifier]
включи [club_identifier] в [league_identifier]
```

**Parameters:**
- `club_identifier` (string, required)
- `league_identifier` (string, required)

**Example:**
```text
>> добави клуб Ботев Враца в лига Втора Лига
Клубът беше добавен в лигата успешно.
```

---

### `get_league_teams`
Show all teams in a league.

**Syntax:**
```text
покажи отбори в лига [league_identifier]
покажи отборите на [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required)

**Example:**
```text
>> покажи отбори в лига Първа Лига
- Левски София (ID: 1)
- ЦСКА София (ID: 2)
...
```

---

### `remove_club_from_league`
Remove a club from a league.

**Syntax:**
```text
премахни отбор [club_identifier] от лига [league_identifier]
премахни клуб [club_identifier] от лига [league_identifier]
изтрий отбор [club_identifier] от лига [league_identifier]
```

**Parameters:**
- `club_identifier` (string, required)
- `league_identifier` (string, required)

**Example:**
```text
>> премахни отбор Ботев Враца от лига Втора Лига
Клубът беше премахнат от лигата успешно.
```

---

### `generate_round_robin`
Generate a schedule for a league.

**Syntax:**
```text
генерирай кръгове за лига [league_identifier]
създай кръгове [league_identifier]
генерирай програма [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required)

**Example:**
```text
>> генерирай кръгове за лига Купа на България
Създадени 6 мача за лига Купа на България.
```

---

### `get_standings`
Show league standings.

**Syntax:**
```text
покажи класиране [league_identifier]
класиране на лига [league_identifier]
```

**Parameters:**
- `league_identifier` (string, required)

**Example:**
```text
>> покажи класиране Първа Лига
# Отбор                 MP  W  D  L  GF:GA   GD  PTS
...
```

---

## Statistics & Metrics

### `club_statistics`
Show club statistics.

**Syntax:**
```text
покажи статистика на клуб [club_identifier]
статистика на клуб [club_identifier]
класиране на [club_identifier]
къде е клуб [club_identifier]
```

**Parameters:**
- `club_identifier` (string, required)

**Example:**
```text
>> покажи статистика на клуб Левски София
Статистика за клуб Левски София:
Игри: 8, Победи: 5, Равни: 2, Загуби: 1,
...
```

---

### `player_statistics`
Show player statistics.

**Syntax:**
```text
покажи статистика на играч [player_identifier]
статистика на играч [player_identifier]
покажи статистика [player_identifier]
```

**Parameters:**
- `player_identifier` (string, required)

**Example:**
```text
>> покажи статистика на играч Александър Колев
Статистика за играч Александър Колев:
Голове: 6, Асистенции: 1,
Появи: 8, Жълти: 1, Червени: 0
```

---

### `player_metrics`
Show advanced player metrics.

**Syntax:**
```text
покажи метрики на играч [player_identifier]
покажи разширени метрики на играч [player_identifier]
метрики на играч [player_identifier]
покажи показатели на играч [player_identifier]
```

**Parameters:**
- `player_identifier` (string, required)

**Example:**
```text
>> покажи метрики на играч Александър Колев
Разширени метрики за Александър Колев:
Мин. (прибл.): 720, Гол/90: 0.75, Асист/90: 0.12
```

---

## Transfers

### `show_transfers_club`
Show transfer history for a club.

**Syntax:**
```text
покажи трансфери на клуб [club_identifier]
трансфери на клуб [club_identifier]
история на трансфери [club_identifier]
```

**Parameters:**
- `club_identifier` (string, required)

**Example:**
```text
>> покажи трансфери на клуб Славия София
Трансфери на клуб 'Славия София':
...
```

---

### `show_transfers_player`
Show transfer history for a player.

**Syntax:**
```text
покажи трансфери на играч [player_identifier]
покажи трансфери на [player_identifier]
трансфери на играч [player_identifier]
история на трансфери [player_identifier]
```

**Parameters:**
- `player_identifier` (string, required)

**Example:**
```text
>> покажи трансфери на играч Самуел Акере
Трансфери на Самуел Акере:
...
```

---

### `transfer_player`
Transfer a player between clubs.

**Syntax:**
```text
трансфер [player_identifier] от [from_club] в [to_club_identifier] [transfer_date] [fee]
трансфер [player_identifier] от [from_club] в [to_club_identifier] [transfer_date]
трансфер [player_identifier] от [from_club] в [to_club_identifier]
трансферирай играч [player_identifier] от [from_club] в клуб [to_club_identifier]
трансферирай играч [player_identifier] от [from_club] в [to_club_identifier]
премести играч [player_identifier] от [from_club] в клуб [to_club_identifier]
премести играч [player_identifier] от [from_club] в [to_club_identifier]
прехвърли играч [player_identifier] от [from_club] в клуб [to_club_identifier]
прехвърли играч [player_identifier] от [from_club] в [to_club_identifier]
трансферирай играч [player_identifier] в клуб [club_identifier]
трансферирай играч [player_identifier] в [club_identifier]
премести играч [player_identifier] в клуб [club_identifier]
премести играч [player_identifier] в [club_identifier]
прехвърли играч [player_identifier] в клуб [club_identifier]
прехвърли играч [player_identifier] в [club_identifier]
трансфер [player_identifier] -> [club_identifier]
```

**Parameters:**
- `player_identifier` (string, required)
- `from_club` (string, conditionally required)
- `to_club_identifier` (string, conditionally required)
- `club_identifier` (string, conditionally required for short forms)
- `transfer_date` (string, optional)
- `fee` (number, optional)

**Examples:**
```text
>> трансфер Самуел Акере от Левски София в Черно море Варна 2025-07-01 500000
Играч 'Самуел Акере' беше трансфериран в клуб 'Черно море Варна'.

>> трансферирай играч Свободен Играч в клуб Арда Кърджали
Играчът беше трансфериран.
```

---

## Prediction

### `predict_match`
Predict match outcome percentages.

**Syntax:**
```text
Prediction [team1] vs [team2]
Predict [team1] vs [team2]
Прогноза [team1] срещу [team2]
Predict [team1] against [team2]
```

**Parameters:**
- `team1` (string, required)
- `team2` (string, required)

**Example:**
```text
>> Prediction Левски София vs ЦСКА София
🏠 Левски София Win: 41%
🤝 Draw: 29%
🛫 ЦСКА София Win: 30%
```

---

## Parameter Reference

### Identifier Resolution

Many commands accept club, player, match, or league identifiers.

Resolution strategy:

1. Exact case-insensitive match
2. Numeric ID match
3. Partial contains fallback in some repositories

### Date Format

Dates use:

```text
YYYY-MM-DD
```

### Position Codes

- `GK` - Goalkeeper
- `DF` - Defender
- `MF` - Midfielder
- `FW` - Forward

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
| `добави играч` | Add player | full_name, club_identifier, position, number, nationality, birth_date, status |
| `покажи играчи` | List players in club | club_identifier |
| `покажи всички играчи` | List all players | - |
| `смени позиция` | Update player position | player_identifier, new_position |
| `смени номер` | Update player number | player_identifier, new_number |
| `смени статус` | Update player status | player_identifier, new_status |
| `изтрий играч` | Delete player | player_identifier |
| `запиши мач` | Record match | home_team, away_team, match_date, home_goals, away_goals |
| `покажи мач` | Show match details | match_id |
| `запиши гол / асист / картон / поява` | Record event | player_identifier, match_id, minute/event_type |
| `покажи събития` | Show match events | match_id |
| `покажи кръг` | Show round matches | round_no, league_name |
| `покажи мачове в лига` | Show fixtures | league_identifier |
| `създай лига` | Create league | league_name, season |
| `добави клуб в лига` | Add club to league | club_identifier, league_identifier |
| `премахни отбор от лига` | Remove club from league | club_identifier, league_identifier |
| `покажи отбори в лига` | List league teams | league_identifier |
| `генерирай кръгове` | Generate fixtures | league_identifier |
| `покажи класиране` | Show league standings | league_identifier |
| `покажи статистика на клуб` | Club statistics | club_identifier |
| `покажи статистика на играч` | Player statistics | player_identifier |
| `покажи метрики на играч` | Advanced player metrics | player_identifier |
| `покажи трансфери на клуб` | Club transfer history | club_identifier |
| `покажи трансфери на играч` | Player transfer history | player_identifier |
| `трансфер / трансферирай играч` | Transfer player | player_identifier, from_club/to_club |
| `Prediction / Predict / Прогноза` | Match prediction | team1, team2 |

---

**Document Version:** 2.0  
**Last Updated:** 2026-06-12  
**Based on:** current `src/chatbot/intents.json` and current router/service behavior
