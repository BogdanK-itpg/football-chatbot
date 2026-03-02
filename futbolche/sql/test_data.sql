PRAGMA foreign_keys = ON;

-- Sample test data for Stage 1
-- Clubs
INSERT INTO clubs (name, city, founded_year) VALUES
('Levski Sofia', 'Sofia', 1914),
('Ludogorets', 'Razgrad', 1945),
('CSKA Sofia', 'Sofia', 1948);

-- Players
INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status) VALUES
(1, 'Ivan Petrov', '1990-05-12', 'Bulgaria', 'FW', 9, 'active'),
(1, 'Georgi Georgiev', '1995-03-02', 'Bulgaria', 'MF', 8, 'active'),
(2, 'Dimitar Ivanov', '1992-11-20', 'Bulgaria', 'DF', 4, 'active'),
(3, 'Alex Smith', '1988-07-07', 'England', 'GK', 1, 'injured');

-- Matches
INSERT INTO matches (home_team_id, away_team_id, home_goals, away_goals, match_date) VALUES
(1, 2, 2, 1, '2025-08-01'),
(3, 1, 0, 3, '2025-08-15');

-- ======= Useful test queries (run against the DB) =======
-- 1) List all clubs
-- SELECT id, name, city, founded_year FROM clubs ORDER BY name;

-- 2) List players in Levski Sofia
-- SELECT p.* FROM players p JOIN clubs c ON p.club_id = c.id WHERE c.name = 'Levski Sofia';

-- 3) Players older than 30 (approximate using year)
-- SELECT full_name, birth_date, (strftime('%Y','now') - strftime('%Y', birth_date)) AS age FROM players WHERE age > 30;

-- 4) Matches and results
-- SELECT m.id, ch.name AS home, ca.name AS away, m.home_goals, m.away_goals, m.match_date
-- FROM matches m JOIN clubs ch ON m.home_team_id = ch.id JOIN clubs ca ON m.away_team_id = ca.id;

-- 5) Referential integrity test: try to insert a player with invalid club_id (should fail)
-- INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status) VALUES (999, 'Bad Player', '2000-01-01', 'Nowhere', 'FW', 99, 'active');

-- End of test data
