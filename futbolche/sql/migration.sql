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
