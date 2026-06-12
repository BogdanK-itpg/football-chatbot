# Demo Database Design

This document defines the intended preset database for project demos.

The goal is not a random seed. The goal is a believable football environment that feels alive the moment the chatbot starts:

- 10 clubs total
- 2 leagues
- a stable core roster in every club
- enough played matches for standings, statistics, transfers, events, and AI prediction demos
- realistic recent form so the showcase does not feel empty

This is a design document for presentation and implementation guidance. It does not change the current codebase by itself.

---

## Demo Principles

Use this database as the default showcase state when the project is presented.

Design goals:

- Every club should already have recognizable players and usable statistics.
- Every league should already have standings and fixtures.
- Every major command should have at least one clean live demo path.
- AI prediction should work immediately for at least 3-4 interesting derbies.
- Transfers, cards, assists, and player metrics should already exist so the project feels complete.

Recommended implementation rules:

- Keep IDs stable between runs for demo consistency.
- Seed enough played matches so every featured club has at least 5 recent matches.
- Seed enough event history so top scorers, assist leaders, and card records look intentional.
- Keep club names, player names, league names, and match pairings Bulgarian-first.

---

## Core Scope

### Clubs

Exactly 10 clubs.

### Leagues

- 1. `Първа Лига` season `2025`
- 2. `Втора Лига` season `2025`

### Club Split

- `Първа Лига`: 5 clubs
- `Втора Лига`: 5 clubs

### Minimum Data Volume

Recommended demo dataset:

- 10 clubs
- 50 players total, 5 core players per club
- 20 played league matches per league
- 8 upcoming matches across both leagues
- 60+ match events total
- 8-12 transfer records

That volume is enough for:

- league tables
- club statistics
- player statistics
- player advanced metrics
- transfer history
- event listing
- AI prediction based on recent form

---

## Club Directory

| ID | Club | City | Founded | League |
|---|---|---:|---:|---|
| 1 | Левски София | София | 1914 | Първа Лига |
| 2 | ЦСКА София | София | 1948 | Първа Лига |
| 3 | Лудогорец Разград | Разград | 1945 | Първа Лига |
| 4 | Ботев Пловдив | Пловдив | 1912 | Първа Лига |
| 5 | Черно море Варна | Варна | 1913 | Първа Лига |
| 6 | Берое Стара Загора | Стара Загора | 1916 | Втора Лига |
| 7 | Локомотив Пловдив | Пловдив | 1926 | Втора Лига |
| 8 | Славия София | София | 1913 | Втора Лига |
| 9 | Арда Кърджали | Кърджали | 1924 | Втора Лига |
| 10 | Ботев Враца | Враца | 1921 | Втора Лига |

---

## League Setup

### Първа Лига (ID: 1, season: 2025)

Members:

- Левски София
- ЦСКА София
- Лудогорец Разград
- Ботев Пловдив
- Черно море Варна

### Втора Лига (ID: 2, season: 2025)

Members:

- Берое Стара Загора
- Локомотив Пловдив
- Славия София
- Арда Кърджали
- Ботев Враца

---

## Club Rosters And Metrics

Each club below has a compact demo-ready core squad. The intention is not to simulate a full real squad of 25 players, but to guarantee enough football substance for every major command.

Legend:

- `Apps` = appearances
- `G` = goals
- `A` = assists
- `YC` = yellow cards
- `RC` = red cards

### 1. Левски София

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Иван Иванов | GK | България | Активен | 8 | 0 | 0 | 1 | 0 |
| 4 | Петър Петров | DF | България | Активен | 8 | 1 | 2 | 3 | 0 |
| 8 | Георги Миланов | MF | България | Активен | 8 | 2 | 4 | 2 | 0 |
| 10 | Асен Митков | MF | България | Активен | 7 | 3 | 3 | 1 | 0 |
| 9 | Александър Колев | FW | България | Активен | 8 | 6 | 1 | 1 | 0 |

Club snapshot:

- Style: proactive possession team
- Strong home record
- Best finisher: Александър Колев

### 2. ЦСКА София

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Георги Димитров | GK | България | Активен | 8 | 0 | 0 | 0 | 0 |
| 3 | Васил Андреев | DF | България | Активен | 8 | 1 | 1 | 4 | 0 |
| 6 | Радослав Недев | MF | България | Активен | 8 | 2 | 2 | 2 | 0 |
| 8 | Димитър Иванов | MF | България | Активен | 8 | 3 | 3 | 1 | 0 |
| 11 | Кристиян Стоянов | FW | България | Активен | 8 | 5 | 2 | 1 | 0 |

Club snapshot:

- Style: balanced, direct transition play
- Strong midfield control
- Main creator: Димитър Иванов

### 3. Лудогорец Разград

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Владислав Стоянов | GK | България | Активен | 8 | 0 | 0 | 0 | 0 |
| 2 | Калоян Стоянов | DF | България | Активен | 8 | 1 | 2 | 1 | 0 |
| 6 | Ивелин Попов | MF | България | Активен | 8 | 2 | 5 | 3 | 0 |
| 8 | Жуан Пауло | MF | Бразилия | Активен | 7 | 2 | 3 | 2 | 0 |
| 10 | Клавдиу Кейсел | FW | Румъния | Активен | 8 | 7 | 1 | 1 | 0 |

Club snapshot:

- Style: best attacking side in the demo DB
- Highest x-factor player: Клавдиу Кейсел
- Reliable title contender

### 4. Ботев Пловдив

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Мартин Камиларов | GK | България | Активен | 8 | 0 | 0 | 0 | 0 |
| 2 | Кирил Симов | DF | България | Активен | 8 | 0 | 1 | 4 | 0 |
| 7 | Радослав Стоянов | MF | България | Активен | 8 | 2 | 2 | 2 | 0 |
| 10 | Самуел Акере | MF | Нигерия | Активен | 7 | 2 | 4 | 1 | 0 |
| 9 | Васил Лечков | FW | България | Активен | 8 | 4 | 1 | 1 | 0 |

Club snapshot:

- Style: energetic wing play
- Good against strong opponents
- Main source of assists: Самуел Акере

### 5. Черно море Варна

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Димитър Манолов | GK | България | Активен | 8 | 0 | 0 | 1 | 0 |
| 3 | Мартин Тодоров | DF | България | Активен | 8 | 1 | 0 | 3 | 0 |
| 4 | Павел Виданов | DF | България | Активен | 8 | 0 | 1 | 4 | 0 |
| 8 | Атанас Пиров | MF | България | Активен | 8 | 1 | 3 | 2 | 0 |
| 11 | Иван Стоянов | FW | България | Активен | 8 | 4 | 2 | 1 | 0 |

Club snapshot:

- Style: disciplined, low-risk football
- Hard to break down
- Strong away results

### 6. Берое Стара Загора

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Атанас Атанасов | GK | България | Активен | 8 | 0 | 0 | 0 | 0 |
| 3 | Иван Иванов | DF | България | Активен | 8 | 1 | 1 | 3 | 0 |
| 7 | Георги Попов | MF | България | Активен | 8 | 2 | 2 | 2 | 0 |
| 8 | Карлос Охене | MF | Гана | Активен | 7 | 1 | 3 | 2 | 0 |
| 11 | Кирил Кирилов | FW | България | Активен | 8 | 5 | 1 | 1 | 0 |

Club snapshot:

- Style: favorite in Втора Лига
- Strong set pieces
- Leading scorer in the second tier

### 7. Локомотив Пловдив

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Иван Колев | GK | България | Активен | 8 | 0 | 0 | 0 | 0 |
| 4 | Петър Стайков | DF | България | Активен | 8 | 0 | 2 | 4 | 0 |
| 6 | Димитър Димитров | MF | България | Активен | 8 | 2 | 2 | 3 | 0 |
| 8 | Мартин Димитров | MF | България | Активен | 8 | 3 | 2 | 1 | 0 |
| 9 | Николай Николов | FW | България | Активен | 8 | 4 | 1 | 2 | 0 |

Club snapshot:

- Style: compact shape, dangerous counters
- Best transition team in the second league demo set

### 8. Славия София

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Никола Николов | GK | България | Активен | 8 | 0 | 0 | 1 | 0 |
| 4 | Владимир Иванов | DF | България | Активен | 8 | 0 | 1 | 5 | 0 |
| 8 | Иван Минчев | MF | България | Активен | 8 | 2 | 3 | 2 | 0 |
| 10 | Христо Попов | MF | България | Активен | 8 | 3 | 4 | 1 | 0 |
| 9 | Денислав Александров | FW | България | Активен | 8 | 5 | 1 | 1 | 0 |

Club snapshot:

- Style: experienced, technical midfield
- Good ball retention
- Very demo-friendly for assists and metrics

### 9. Арда Кърджали

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Иван Караджов | GK | България | Активен | 8 | 0 | 0 | 0 | 0 |
| 2 | Милчо Ангелов | DF | България | Активен | 8 | 1 | 1 | 2 | 0 |
| 7 | Станислав Иванов | MF | България | Активен | 8 | 3 | 2 | 1 | 0 |
| 8 | Пламен Крумов | MF | България | Активен | 8 | 1 | 3 | 3 | 0 |
| 10 | Тонислав Йорданов | FW | България | Активен | 8 | 4 | 2 | 1 | 0 |

Club snapshot:

- Style: vertical, energetic, direct
- Strong in open games

### 10. Ботев Враца

| No | Player | Pos | Nationality | Status | Apps | G | A | YC | RC |
|---:|---|---|---|---|---:|---:|---:|---:|---:|
| 1 | Христо Бонев | GK | България | Активен | 8 | 0 | 0 | 0 | 0 |
| 5 | Валери Домовчийски | DF | България | Активен | 8 | 1 | 0 | 4 | 0 |
| 6 | Красимир Тодоров | MF | България | Активен | 8 | 1 | 2 | 3 | 0 |
| 8 | Петър Атанасов | MF | България | Активен | 8 | 2 | 2 | 1 | 0 |
| 9 | Владислав Василев | FW | България | Активен | 8 | 3 | 1 | 2 | 0 |

Club snapshot:

- Style: physical, defensive, resilient
- Useful demo club for survival-story narratives

---

## Preset League Tables

These tables are the intended visible state when the project is shown.

### Първа Лига - season 2025

| Pos | Club | MP | W | D | L | GF | GA | GD | PTS |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Лудогорец Разград | 8 | 6 | 1 | 1 | 18 | 7 | +11 | 19 |
| 2 | Левски София | 8 | 5 | 2 | 1 | 15 | 8 | +7 | 17 |
| 3 | ЦСКА София | 8 | 4 | 2 | 2 | 14 | 10 | +4 | 14 |
| 4 | Черно море Варна | 8 | 3 | 2 | 3 | 10 | 10 | 0 | 11 |
| 5 | Ботев Пловдив | 8 | 2 | 1 | 5 | 9 | 15 | -6 | 7 |

### Втора Лига - season 2025

| Pos | Club | MP | W | D | L | GF | GA | GD | PTS |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Берое Стара Загора | 8 | 5 | 2 | 1 | 14 | 7 | +7 | 17 |
| 2 | Славия София | 8 | 4 | 3 | 1 | 13 | 8 | +5 | 15 |
| 3 | Локомотив Пловдив | 8 | 4 | 1 | 3 | 11 | 10 | +1 | 13 |
| 4 | Арда Кърджали | 8 | 3 | 2 | 3 | 10 | 10 | 0 | 11 |
| 5 | Ботев Враца | 8 | 1 | 2 | 5 | 7 | 14 | -7 | 5 |

---

## Preset Match Catalog

For demo purposes, every club should already have enough completed matches for standings, club statistics, player statistics, and AI prediction.

Recommended visible match IDs:

| Match ID | League | Round | Date | Home | Score | Away |
|---:|---|---:|---|---|---|---|
| 1 | Първа Лига | 1 | 2025-08-01 | Левски София | 2-1 | ЦСКА София |
| 2 | Първа Лига | 1 | 2025-08-02 | Лудогорец Разград | 3-0 | Ботев Пловдив |
| 3 | Първа Лига | 1 | 2025-08-03 | Черно море Варна | 1-1 | Левски София |
| 4 | Първа Лига | 2 | 2025-08-08 | ЦСКА София | 2-0 | Ботев Пловдив |
| 5 | Първа Лига | 2 | 2025-08-09 | Лудогорец Разград | 2-2 | Черно море Варна |
| 6 | Първа Лига | 3 | 2025-08-15 | Левски София | 1-0 | Лудогорец Разград |
| 7 | Първа Лига | 3 | 2025-08-16 | Ботев Пловдив | 1-2 | Черно море Варна |
| 8 | Първа Лига | 4 | 2025-08-22 | ЦСКА София | 2-2 | Лудогорец Разград |
| 9 | Втора Лига | 1 | 2025-08-01 | Берое Стара Загора | 2-0 | Ботев Враца |
| 10 | Втора Лига | 1 | 2025-08-02 | Славия София | 2-1 | Локомотив Пловдив |
| 11 | Втора Лига | 1 | 2025-08-03 | Арда Кърджали | 1-1 | Берое Стара Загора |
| 12 | Втора Лига | 2 | 2025-08-09 | Локомотив Пловдив | 1-0 | Ботев Враца |
| 13 | Втора Лига | 2 | 2025-08-10 | Славия София | 2-0 | Арда Кърджали |
| 14 | Втора Лига | 3 | 2025-08-17 | Берое Стара Загора | 1-1 | Локомотив Пловдив |

Recommended future fixtures for live demo commands:

| Match ID | League | Round | Date | Home | Away | Status |
|---:|---|---:|---|---|---|---|
| 21 | Първа Лига | 5 | 2025-09-01 | Левски София | Ботев Пловдив | Предстоящ |
| 22 | Първа Лига | 5 | 2025-09-02 | ЦСКА София | Черно море Варна | Предстоящ |
| 23 | Първа Лига | 5 | 2025-09-03 | Лудогорец Разград | Левски София | Предстоящ |
| 31 | Втора Лига | 5 | 2025-09-01 | Берое Стара Загора | Славия София | Предстоящ |
| 32 | Втора Лига | 5 | 2025-09-02 | Локомотив Пловдив | Арда Кърджали | Предстоящ |

---

## Event Design

Seed enough events so the event log is always interesting.

Recommended minimum event types already present in the DB:

- goals
- assists
- yellow cards
- red cards
- appearances

Recommended showcase event sequence for match ID 1:

- `23' - ГОЛ - Александър Колев`
- `44' - АСИСТЕНЦИЯ - Георги Миланов`
- `55' - ЖК - Васил Андреев`
- `68' - ГОЛ - Кристиян Стоянов`
- `81' - ГОЛ - Александър Колев`

This single match can power:

- `show_match`
- `show_events`
- `player_statistics`
- `player_metrics`
- `club_statistics`

---

## Transfer Design

Preset transfers should feel believable and should support both player-centric and club-centric history demos.

Recommended seeded transfer history:

| Date | Player | From | To | Fee |
|---|---|---|---|---:|
| 2025-01-10 | Самуел Акере | Ботев Пловдив | Левски София | 850000 |
| 2025-01-14 | Милчо Ангелов | Арда Кърджали | Ботев Враца | 120000 |
| 2025-01-22 | Жуан Пауло | Лудогорец Разград | Черно море Варна | 600000 |
| 2025-02-03 | Петър Атанасов | Ботев Враца | Славия София | 150000 |
| 2025-02-12 | Станислав Иванов | Арда Кърджали | Берое Стара Загора | 300000 |
| 2025-02-17 | Владимир Иванов | Славия София | Локомотив Пловдив | 0 |

Recommended free-agent scenario:

- one additional player starts without club and is later signed by Арда Кърджали

---

## AI Prediction Readiness

To make `predict_match` work reliably during a demo:

- every featured club must have at least 5 recent matches
- at least one league must have enough completed results for meaningful form
- featured pairings must be from the same league

Recommended featured prediction pairings:

- `Левски София vs ЦСКА София`
- `Лудогорец Разград vs Черно море Варна`
- `Берое Стара Загора vs Славия София`

---

## Suggested Demo Flow

If the project is shown live, this order feels natural:

1. Show clubs
2. Show one league and its teams
3. Show standings
4. Show fixtures and one match
5. Show events from that match
6. Show one club’s statistics
7. Show one player’s statistics and metrics
8. Show transfer history
9. Run one prediction
10. Add one club, one player, one match, and one event live

---

## Full Demo Scenarios

This section gives one example input/output pair for every current command intent so the presentation can run without improvisation.

### 1. `help`

**Input**
```text
помощ
```

**Output**
```text
Налични команди:

Клубове:
- добави клуб [club_name]
- покажи всички клубове
- промени клуб [club_name] на [new_name]
- изтрий клуб [club_name]

Играчи:
- добави играч [full_name] в клуб [club_identifier] позиция [position] номер [number] националност [nationality] дата на раждане [birth_date] статус [status]
- покажи играчи на клуб [club_identifier]
- покажи всички играчи
...
```

### 2. `exit`

**Input**
```text
изход
```

**Output**
```text
До скоро!
```

### 3. `create_league`

**Input**
```text
създай лига Купа на България сезон 2025
```

**Output**
```text
Лига 'Купа на България' (2025) беше създадена успешно.
```

### 4. `remove_club_from_league`

**Input**
```text
премахни отбор Ботев Враца от лига Втора Лига
```

**Output**
```text
Клубът беше премахнат от лигата успешно.
```

### 5. `add_club_to_league`

**Input**
```text
добави клуб Ботев Враца в лига Втора Лига
```

**Output**
```text
Клубът беше добавен в лигата успешно.
```

### 6. `get_league_teams`

**Input**
```text
покажи отбори в лига Първа Лига
```

**Output**
```text
- Левски София (ID: 1)
- ЦСКА София (ID: 2)
- Лудогорец Разград (ID: 3)
- Ботев Пловдив (ID: 4)
- Черно море Варна (ID: 5)
```

### 7. `generate_round_robin`

**Input**
```text
генерирай кръгове за лига Купа на България
```

**Output**
```text
Създадени 6 мача за лига Купа на България.
```

### 8. `get_standings`

**Input**
```text
покажи класиране Първа Лига
```

**Output**
```text
 # Отбор                 MP  W  D  L  GF:GA   GD  PTS
 1. Лудогорец Разград     8  6  1  1  18:7   +11   19
 2. Левски София          8  5  2  1  15:8    +7   17
 3. ЦСКА София            8  4  2  2  14:10   +4   14
 4. Черно море Варна      8  3  2  3  10:10    0   11
 5. Ботев Пловдив         8  2  1  5   9:15   -6    7
```

### 9. `get_fixtures`

**Input**
```text
покажи мачове в лига Първа Лига
```

**Output**
```text
2025-08-01: Левски София vs ЦСКА София (2-1)
2025-08-02: Лудогорец Разград vs Ботев Пловдив (3-0)
2025-08-03: Черно море Варна vs Левски София (1-1)
2025-09-01: Левски София vs Ботев Пловдив (None-None)
```

### 10. `delete_player`

**Input**
```text
изтрий играч 50
```

**Output**
```text
Играч с ID 50 беше изтрит.
```

### 11. `list_all_players`

**Input**
```text
покажи всички играчи
```

**Output**
```text
ID  Име                   Клуб                    Поз  №   Националност   Р. Дата     Статус
----------------------------------------------------------------------------------------------
1   Иван Иванов           Левски София            GK   1   България        1995-03-15  Активен
2   Петър Петров          Левски София            DF   4   България        1998-07-22  Активен
...
```

### 12. `add_club`

**Input**
```text
добави клуб Дунав Русе
```

**Output**
```text
Клуб 'Дунав Русе' беше добавен успешно.
```

### 13. `list_clubs`

**Input**
```text
покажи клубове
```

**Output**
```text
1. Левски София
2. ЦСКА София
3. Лудогорец Разград
4. Ботев Пловдив
5. Черно море Варна
6. Берое Стара Загора
7. Локомотив Пловдив
8. Славия София
9. Арда Кърджали
10. Ботев Враца
```

### 14. `delete_club`

**Input**
```text
изтрий клуб Дунав Русе
```

**Output**
```text
Клуб 'Дунав Русе' беше изтрит.
```

### 15. `update_club`

**Input**
```text
промени клуб Ботев Враца на Ботев Враца 1921
```

**Output**
```text
Клубът беше успешно обновен.
```

### 16. `add_player`

**Input**
```text
добави играч Николай Георгиев в клуб Левски София позиция FW номер 19 националност България дата на раждане 2001-04-17 статус Активен
```

**Output**
```text
Играч 'Николай Георгиев' беше добавен успешно.
```

### 17. `list_players`

**Input**
```text
покажи играчи на клуб Левски София
```

**Output**
```text
ID  Име                   Клуб                    Поз  №   Националност   Р. Дата     Статус
----------------------------------------------------------------------------------------------
1   Иван Иванов           Левски София            GK   1   България        1995-03-15  Активен
2   Петър Петров          Левски София            DF   4   България        1998-07-22  Активен
3   Георги Миланов        Левски София            MF   8   България        1992-02-19  Активен
4   Асен Митков           Левски София            MF   10  България        2003-03-12  Активен
5   Александър Колев      Левски София            FW   9   България        1992-12-08  Активен
```

### 18. `update_player_position`

**Input**
```text
смени позиция на Александър Колев на MF
```

**Output**
```text
Позицията на играч с ID 5 беше обновена на MF.
```

### 19. `update_player_number`

**Input**
```text
смени номер на Александър Колев на 99
```

**Output**
```text
Номерът на играч с ID 5 беше сменен на 99.
```

### 20. `update_player_status`

**Input**
```text
смени статус на Александър Колев на Контузен
```

**Output**
```text
Статусът на играч с ID 5 беше обновен на 'Контузен'.
```

### 21. `club_statistics`

**Input**
```text
покажи статистика на клуб Левски София
```

**Output**
```text
Статистика за клуб Левски София:
Игри: 8, Победи: 5, Равни: 2, Загуби: 1,
Голове за: 15, Голове срещу: 8, Голова разлика: 7, Точки: 17
```

### 22. `player_statistics`

**Input**
```text
покажи статистика на играч Александър Колев
```

**Output**
```text
Статистика за играч Александър Колев:
Голове: 6, Асистенции: 1,
Появи: 8, Жълти: 1, Червени: 0
```

### 23. `player_metrics`

**Input**
```text
покажи метрики на играч Александър Колев
```

**Output**
```text
Разширени метрики за Александър Колев:
Мин. (прибл.): 720, Гол/90: 0.75, Асист/90: 0.12
```

### 24. `show_transfers_club`

**Input**
```text
покажи трансфери на клуб Славия София
```

**Output**
```text
Трансфери на клуб 'Славия София':
  2025-02-03: Петър Атанасов Ботев Враца → Славия София (пристига), такса: 150000.00
  2025-02-17: Владимир Иванов Славия София → Локомотив Пловдив (напуска), такса: 0.00
```

### 25. `show_transfers_player`

**Input**
```text
покажи трансфери на играч Самуел Акере
```

**Output**
```text
Трансфери на Самуел Акере:
  2025-01-10: Ботев Пловдив → Левски София, такса: 850000.00
```

### 26. `transfer_player`

**Input**
```text
трансфер Самуел Акере от Левски София в Черно море Варна 2025-07-01 500000
```

**Output**
```text
Играч 'Самуел Акере' беше трансфериран в клуб 'Черно море Варна'.
```

### 27. `show_events`

**Input**
```text
покажи събития 1
```

**Output**
```text
23' - ГОЛ - Александър Колев
44' - АСИСТЕНЦИЯ - Георги Миланов
55' - ЖК - Васил Андреев
68' - ГОЛ - Кристиян Стоянов
81' - ГОЛ - Александър Колев
```

### 28. `show_round`

**Input**
```text
покажи кръг 1 Първа Лига
```

**Output**
```text
--- Кръг 1 ---
ID:1 | 2025-08-01 | Левски София 2:1 ЦСКА София | ИЗИГРАН
ID:2 | 2025-08-02 | Лудогорец Разград 3:0 Ботев Пловдив | ИЗИГРАН
ID:3 | 2025-08-03 | Черно море Варна 1:1 Левски София | ИЗИГРАН
```

### 29. `record_match`

**Input**
```text
запиши мач Берое Стара Загора срещу Арда Кърджали дата 2025-09-12 резултат 2-1 лига Втора Лига кръг 6
```

**Output**
```text
Мачът беше записан с ID 41.
```

### 30. `show_match`

**Input**
```text
покажи мач 1
```

**Output**
```text
2025-08-01: Левски София 2-1 ЦСКА София
```

### 31. `predict_match`

**Input**
```text
Prediction Левски София vs ЦСКА София
```

**Output**
```text
🏠 Левски София Win: 41%
🤝 Draw: 29%
🛫 ЦСКА София Win: 30%
```

### 32. `record_event`

**Input**
```text
запиши гол Александър Колев в мач 21 минута 73
```

**Output**
```text
Събитието беше записано успешно.
```

---

## Final Recommendation

If this project is shown publicly, the demo DB should feel like a mid-season Bulgarian football world, not a technical sandbox.

That means:

- recognizable club identities
- believable league tables
- star players with real output
- transfer stories
- enough history for prediction and metrics
- one clean scenario for every command

This file should be treated as the target showcase database spec.
