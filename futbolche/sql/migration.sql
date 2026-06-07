-- Migration: add missing columns to existing database
-- This script is safe to run on existing databases.

-- Add round_no to matches
ALTER TABLE matches ADD COLUMN round_no INTEGER DEFAULT NULL;

-- Add is_played to matches
ALTER TABLE matches ADD COLUMN is_played INTEGER NOT NULL DEFAULT 0;

-- Set is_played = 1 for matches that have scores recorded
UPDATE matches SET is_played = 1 WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL;

-- Add club_id to events
ALTER TABLE events ADD COLUMN club_id INTEGER DEFAULT NULL REFERENCES clubs(id);

-- Backfill club_id for existing events from the players table
UPDATE events SET club_id = (SELECT club_id FROM players WHERE players.id = events.player_id) WHERE club_id IS NULL AND player_id IS NOT NULL;

-- Add is_own_goal to events
ALTER TABLE events ADD COLUMN is_own_goal INTEGER NOT NULL DEFAULT 0;

-- Add created_at to events
ALTER TABLE events ADD COLUMN created_at TEXT NOT NULL DEFAULT (datetime('now'));

-- Add card_type to events (Y/R for cards, NULL for non-cards)
ALTER TABLE events ADD COLUMN card_type TEXT DEFAULT NULL CHECK(card_type IS NULL OR card_type IN ('Y','R'));

-- Backfill card_type from event_type
UPDATE events SET card_type = 'Y' WHERE event_type = 'yellow';
UPDATE events SET card_type = 'R' WHERE event_type = 'red';

-- Add created_at and unique constraint to leagues
ALTER TABLE leagues ADD COLUMN created_at TEXT NOT NULL DEFAULT (datetime('now'));
CREATE UNIQUE INDEX IF NOT EXISTS idx_leagues_name_season ON leagues(name, season);

-- Add joined_at to league_teams
ALTER TABLE league_teams ADD COLUMN joined_at TEXT NOT NULL DEFAULT (datetime('now'));

-- Add unique constraint on matches to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_matches_league_round_teams
    ON matches(league_id, round_no, home_team_id, away_team_id);

-- =====================================
-- Migration: add transfers table
-- =====================================
CREATE TABLE IF NOT EXISTS transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    from_club_id INTEGER DEFAULT NULL,
    to_club_id INTEGER NOT NULL,
    transfer_date TEXT NOT NULL,
    fee REAL DEFAULT NULL,
    note TEXT DEFAULT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    FOREIGN KEY (from_club_id) REFERENCES clubs(id) ON DELETE SET NULL,
    FOREIGN KEY (to_club_id) REFERENCES clubs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transfers_player_id ON transfers(player_id);
CREATE INDEX IF NOT EXISTS idx_transfers_from_club_id ON transfers(from_club_id);
CREATE INDEX IF NOT EXISTS idx_transfers_to_club_id ON transfers(to_club_id);
CREATE INDEX IF NOT EXISTS idx_transfers_transfer_date ON transfers(transfer_date);
