PRAGMA foreign_keys = ON;

-- Seed transfers for testing
-- References clubs (1-8) and players (1-38) from the default seed data

-- Transfer 1: Иван Иванов (id=1) from Левски София (club=1) to ЦСКА София (club=2), 2026-01-15, no fee
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (1, 1, 2, '2026-01-15', NULL, 'Директен трансфер');

-- Transfer 2: Петър Петров (id=2) from Левски София (club=1) to Ботев Пловдив (club=3), 2026-02-01, fee 50000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (2, 1, 3, '2026-02-01', 50000, 'Трансфер с такса');

-- Transfer 3: Георги Димитров (id=6) from ЦСКА София (club=2) to Лудогорец Разград (club=4), 2026-03-10, fee 120000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (6, 2, 4, '2026-03-10', 120000, 'Преминаване в Лудогорец');

-- Transfer 4: Димитър Иванов (id=7) from ЦСКА София (club=2) to Черно море Варна (club=5), 2026-03-20, no fee
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (7, 2, 5, '2026-03-20', NULL, NULL);

-- Transfer 5: Васил Лечков (id=14) from Ботев Пловдив (club=3) to Локомотив Пловдив (club=7), 2026-04-05, fee 75000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (14, 3, 7, '2026-04-05', 75000, 'Вътрешноградски трансфер Пловдив');

-- Transfer 6: Кристиян Стоянов (id=8) from ЦСКА София (club=2) to Спартак Варна (club=6), 2026-05-01, fee 30000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (8, 2, 6, '2026-05-01', 30000, 'Трансфер в Спартак Варна');
