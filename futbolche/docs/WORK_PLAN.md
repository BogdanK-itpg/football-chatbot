# Work Plan: Live Event Recording with Score & `is_played` Guard

## Problem Statement

When a round-robin schedule is generated for a league, matches are created with `is_played = 0` and `home_goals = NULL`, `away_goals = NULL`. Currently, the `record_event` flow:

1. Inserts an event row into the `events` table (goal, assist, card, etc.)
2. Does **NOT** update `home_goals` / `away_goals` in the `matches` table when a goal is recorded
3. Does **NOT** check `is_played` — events can be added even after a match is marked complete
4. Does **NOT** integrate existing validators (`validate_no_duplicate_result`, `validate_player_in_match`, etc.)

The goal: when events are added to a live (unplayed) match, the score updates in real time, and once `is_played = 1`, no further events can be added.

---

## Current State (Baseline)

| Component | What it does now | Gap |
|-----------|-----------------|-----|
| `matches_repo.increment_score()` | Exists — increments home or away goals | **Unused** nowhere called |
| `matches_repo.is_played()` | Exists — returns bool | Called only by `validate_no_duplicate_result` |
| `validators.py` | Has `validate_no_duplicate_result`, `validate_player_in_match`, `validate_no_goal_after_red`, `validate_card_allowed`, `validate_minute` | **Not wired** into `record_event` in router |
| `router.py` (record_event) | Resolves player → club, calls `matches.record_event()` | No validation, no score update |
| `matches_service.record_event()` | Only inserts event row | No score update, no `is_played` check |
| `matches_service.record_match()` | Sets `is_played=1` when both scores provided | Only on initial creation |

---

## Proposed Changes

### Phase 1: Validation & Guard Layer (in `matches_service.py`)

Add a new function `record_event_safe()` that wraps `record_event` with all checks:

```python
def record_event_safe(match_id, player_id, club_id, event_type, minute=None, card_type=None, is_own_goal=0):
```

**Checks to perform (in order):**

1. **Match exists** — `matches_repo.exists(match_id)` → error if not
2. **Match is not played** — `matches_repo.is_played(match_id)` → error if already played (`is_played = 1`)
3. **Minute is valid** — `validate_minute(minute)` → error if invalid (for events that require minute)
4. **Player belongs to match** — `validate_player_in_match(player_id, match_id)` → error if not
5. **For goals**: `validate_no_goal_after_red(player_id, match_id)` → error if player already sent off
6. **For cards**: `validate_card_allowed(player_id, match_id, card_type)` → error if rules violated

After all checks pass:
- Call `events_repo.create(...)` to insert the event
- **If `event_type == 'goal'`**: determine if player's `club_id` is home or away, call `matches_repo.increment_score(match_id, is_home)` to update score

### Phase 2: Update Router

Replace direct call to `matches.record_event()` with `matches.record_event_safe()` in `router.py` (line 258).

The router already resolves `player_id` and `club_id` — pass these through.

### Phase 3: Wire `card_type` from NLU to Service

Current NLU for `record_event` captures `event_type` but doesn't map `"жълт картон"` → `event_type="yellow", card_type="Y"` and `"червен картон"` → `event_type="red", card_type="R"`.

In `router.py`, add mapping:
- `event_type == "жълт картон"` → type=`yellow`, card=`Y`
- `event_type == "червен картон"` → type=`red`, card=`R`
- `event_type == "гол"` → type=`goal`, card=`None`
- `event_type == "асист"` → type=`assist`, card=`None`
- `event_type == "поява"` → type=`appearance`, card=`None`

### Phase 4: Add "End Match" / "Close Match" Intent

Add a new intent to close a match (set `is_played = 1`) manually.

**NLU Pattern (in `intents.json`):**
```json
{
  "tag": "end_match",
  "patterns": [
    "приключи мач [match_id]",
    "закрий мач [match_id]",
    "завърши мач [match_id]"
  ]
}
```

**New function in `matches_service.py`:**
```python
def end_match(match_id):
    if not matches_repo.exists(match_id):
        return "Мачът не съществува."
    if matches_repo.is_played(match_id):
        return "Мачът вече е приключен."
    matches_repo.set_played(match_id)
    return f"Мач ID {match_id} е приключен."
```

**Route in `router.py`:** Add handler for `end_match` intent.

### Phase 5: Integration — Auto-close Match on Final Whistle (Optional Enhancement)

If an event is recorded with `minute >= 90` (or `minute == 90` for stoppage time), automatically set `is_played = 1` inside `record_event_safe`. This can be a configurable behavior.

### Phase 6: Update `show_round` Display

Currently shows `home_goals` / `away_goals` from the DB. After Phase 1, goals will be auto-incremented, so the display will reflect live scoring without changes. No modification needed here — it'll "just work".

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/services/matches_service.py` | Add `record_event_safe()`, add `end_match()`, add `record_event_safe` with validation + score update |
| `src/chatbot/router.py` | Replace `record_event` call with `record_event_safe`, add `card_type` mapping, add `end_match` route |
| `src/chatbot/intents.json` | Add `end_match` intent patterns |
| `src/validators.py` | Minor: no changes needed (validators already exist) |
| `src/repositories/matches_repo.py` | Minor: no changes needed (all functions exist) |
| `src/repositories/events_repo.py` | Minor: no changes needed |

---

## Flow Diagram

```
User: "запиши гол Александър Колев в мач 5 минута 23"
                    │
                    ▼
         NLU → intent: "record_event"
         params: { player_identifier, match_id, minute, event_type: "гол" }
                    │
                    ▼
         Router (router.py):
           - Resolve player_name → player_id
           - Get player's club_id
           - Map "гол" → event_type="goal"
           - Resolve match_id to int
                    │
                    ▼
         matches_service.record_event_safe(match_id, player_id, club_id, "goal", minute=23)
                    │
                    ├─► 1. match exists?           ── NO → error
                    ├─► 2. is_played == 0?          ── NO → "Мачът вече е приключен"
                    ├─► 3. minute valid?            ── NO → error
                    ├─► 4. player in match?         ── NO → error
                    ├─► 5. player not red-carded?   ── NO → error
                    │
                    ▼
         ┌─► events_repo.create(...)      ← insert event row
         └─► matches_repo.increment_score(match_id, is_home=True)
                    │
                    ▼
         Response: "Събитието беше записано успешно."
```

```
User: "приключи мач 5"
         │
         ▼
         matches_service.end_match(5)
           ├─► matches_repo.exists(5)?     ── NO → error
           ├─► matches_repo.is_played(5)?  ── YES → "Вече е приключен"
           └─► matches_repo.set_played(5)  ── OK → "Мач ID 5 е приключен"
```

---

## Edge Cases to Handle

| Scenario | Expected Behavior |
|----------|------------------|
| Add goal after `is_played=1` | Rejected: "Мачът вече е приключен" |
| Add goal for player not in match | Rejected: "Играчът не участва в този мач" |
| Add goal after player got red card | Rejected: "Играчът е получил червен картон" |
| Add second yellow (should be red) | Rejected unless card_type='R' |
| Add event to non-existent match | Rejected: "Мачът не съществува" |
| Close already-closed match | Rejected: "Мачът вече е приключен" |
| Goal in 120th minute auto-closes match | Auto-set `is_played=1` (optional Phase 5) |
| Multiple goals same player | Allowed (hat-trick etc.) — no restriction |

---

## Testing Strategy

1. **Unit tests** for `record_event_safe`:
   - Rejects event on played match
   - Rejects event on non-existent match
   - Rejects goal from player not in match
   - Rejects goal after red card
   - Accepts valid goal and increments score

2. **Unit tests** for `end_match`:
   - Marks unplayed match as played
   - Rejects already played match
   - Rejects non-existent match

3. **Integration** (via chatbot):
   - Full flow: generate round robin → record goal → verify score → end match → verify events rejected

4. **Existing tests**: Run `test_repositories.py`, `test_services_handlers.py` to ensure no regressions

---

## Dependencies (None)

All changes use existing stdlib modules only. No new packages required.
