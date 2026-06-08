PRAGMA foreign_keys = ON;

-- Seed transfers for testing
-- References clubs (1-18) and players (1-90) from the default seed data

-- === Първа Лига transfers ===

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

-- Transfer 7: Ивелин Попов (id=18) from Лудогорец (club=4) to Берое (club=8), 2026-06-01, fee 90000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (18, 4, 8, '2026-06-01', 90000, 'Завръщане в Берое');

-- Transfer 8: Никола Николов (id=41) from Славия София (club=9) to Левски София (club=1), 2026-06-15, fee 200000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (41, 9, 1, '2026-06-15', 200000, 'Преминаване в Левски');

-- Transfer 9: Спас Георгиев (id=49) from Локомотив София (club=10) to ЦСКА София (club=2), 2026-07-01, fee 150000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (49, 10, 2, '2026-07-01', 150000, 'Трансфер в ЦСКА');

-- === Втора Лига transfers ===

-- Transfer 10: Станислав Иванов (id=53) from Арда Кърджали (club=11) to Лудогорец (club=4), 2026-07-10, fee 350000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (53, 11, 4, '2026-07-10', 350000, 'Преминаване в Лудогорец');

-- Transfer 11: Кирил Десподов (id=69) from ЦСКА 1948 (club=14) to Локомотив Пловдив (club=7), 2026-07-20, fee 60000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (69, 14, 7, '2026-07-20', 60000, 'Трансфер в Локомотив Пд');

-- Transfer 12: Пламен Иванов (id=82) from Етър (club=17) to Ботев Пловдив (club=3), 2026-08-01, fee 45000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (82, 17, 3, '2026-08-01', 45000, 'Преминаване в Ботев');

-- Transfer 13: Атанас Илиев (id=74) from Хебър (club=15) to Черно море (club=5), 2026-08-05, fee 25000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (74, 15, 5, '2026-08-05', 25000, NULL);

-- Transfer 14: Павел Петков (id=89) from Септември (club=18) to Славия София (club=9), 2026-08-15, fee 10000
INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note)
VALUES (89, 18, 9, '2026-08-15', 10000, 'Трансфер в Славия');
