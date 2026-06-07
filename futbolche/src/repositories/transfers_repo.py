from db import fetch_one, fetch_all, execute


def create(player_id, from_club_id, to_club_id, transfer_date, fee=None, note=None, conn=None):
    return execute(
        "INSERT INTO transfers (player_id, from_club_id, to_club_id, transfer_date, fee, note) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (player_id, from_club_id, to_club_id, transfer_date, fee, note),
        conn=conn
    )


def get_by_id(transfer_id):
    return fetch_one(
        "SELECT t.*, "
        "p.full_name as player_name, "
        "fc.name as from_club_name, "
        "tc.name as to_club_name "
        "FROM transfers t "
        "JOIN players p ON t.player_id = p.id "
        "LEFT JOIN clubs fc ON t.from_club_id = fc.id "
        "JOIN clubs tc ON t.to_club_id = tc.id "
        "WHERE t.id = ?",
        (transfer_id,)
    )


def get_by_player(player_id):
    return fetch_all(
        "SELECT t.*, "
        "p.full_name as player_name, "
        "fc.name as from_club_name, "
        "tc.name as to_club_name "
        "FROM transfers t "
        "JOIN players p ON t.player_id = p.id "
        "LEFT JOIN clubs fc ON t.from_club_id = fc.id "
        "JOIN clubs tc ON t.to_club_id = tc.id "
        "WHERE t.player_id = ? "
        "ORDER BY t.transfer_date DESC",
        (player_id,)
    )


def get_by_club(club_id):
    return fetch_all(
        "SELECT t.*, "
        "p.full_name as player_name, "
        "fc.name as from_club_name, "
        "tc.name as to_club_name "
        "FROM transfers t "
        "JOIN players p ON t.player_id = p.id "
        "LEFT JOIN clubs fc ON t.from_club_id = fc.id "
        "JOIN clubs tc ON t.to_club_id = tc.id "
        "WHERE t.from_club_id = ? OR t.to_club_id = ? "
        "ORDER BY t.transfer_date DESC",
        (club_id, club_id)
    )


def get_all():
    return fetch_all(
        "SELECT t.*, "
        "p.full_name as player_name, "
        "fc.name as from_club_name, "
        "tc.name as to_club_name "
        "FROM transfers t "
        "JOIN players p ON t.player_id = p.id "
        "LEFT JOIN clubs fc ON t.from_club_id = fc.id "
        "JOIN clubs tc ON t.to_club_id = tc.id "
        "ORDER BY t.transfer_date DESC"
    )
