from db import execute_query
from datetime import datetime, date
import re

def validate_position(position):
    """Validate position is one of GK, DF, MF, FW"""
    return position in ['GK', 'DF', 'MF', 'FW']

def validate_number(number):
    """Validate jersey number is between 1 and 99"""
    try:
        num = int(number)
        return 1 <= num <= 99
    except (ValueError, TypeError):
        return False

def validate_birth_date(birth_date):
    """Validate birth date format (YYYY-MM-DD) and not in future"""
    try:
        # Parse the date
        parsed_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        # Check if date is not in the future
        today = date.today()
        return parsed_date <= today
    except (ValueError, TypeError):
        return False

def get_club_id(club_identifier):
    """Get club ID by name or ID. Returns None if not found."""
    # Try to find by name first
    result = execute_query(
        "SELECT id FROM clubs WHERE LOWER(name) = LOWER(?)",
        (club_identifier,),
        fetch=True
    )
    if result:
        return result[0]['id']
    
    # Try to find by ID if it's a number
    try:
        club_id = int(club_identifier)
        result = execute_query(
            "SELECT id FROM clubs WHERE id = ?",
            (club_id,),
            fetch=True
        )
        if result:
            return result[0]['id']
    except ValueError:
        pass
    
    return None

def get_player_id(player_identifier):
    """Get player ID by full_name or ID. Returns None if not found."""
    # Try to find by full_name first
    result = execute_query(
        "SELECT id FROM players WHERE LOWER(full_name) = LOWER(?)",
        (player_identifier,),
        fetch=True
    )
    if result:
        return result[0]['id']
    
    # Try to find by ID if it's a number
    try:
        player_id = int(player_identifier)
        result = execute_query(
            "SELECT id FROM players WHERE id = ?",
            (player_id,),
            fetch=True
        )
        if result:
            return result[0]['id']
    except ValueError:
        pass
    
    return None

def add_player(club_id, full_name, birth_date, nationality, position, number, status):
    """Add a new player with validation"""
    # Validate all fields
    if not full_name or full_name.strip() == "":
        return "Името на играча не може да бъде празно."
    
    if not validate_birth_date(birth_date):
        return "Невалидна дата на раждане. Използвайте формат YYYY-MM-DD и дата не може да бъде в бъдещето."
    
    if not nationality or nationality.strip() == "":
        return "Националността не може да бъде празна."
    
    if not validate_position(position):
        return "Невалидна позиция. Използвайте една от: GK, DF, MF, FW."
    
    if not validate_number(number):
        return "Невалиден номер. Номерът трябва да бъде между 1 и 99."
    
    if not status or status.strip() == "":
        return "Статусът не може да бъде празен."
    
    # Check if club exists
    club = execute_query("SELECT id FROM clubs WHERE id = ?", (club_id,), fetch=True)
    if not club:
        return f"Клуб с ID {club_id} не съществува."
    
    # Check if player with same name already exists for this club
    existing = execute_query(
        "SELECT * FROM players WHERE LOWER(full_name) = LOWER(?) AND club_id = ?",
        (full_name, club_id),
        fetch=True
    )
    if existing:
        return f"Играч с име '{full_name}' вече съществува в този клуб."
    
    # Insert player
    try:
        execute_query(
            """INSERT INTO players (club_id, full_name, birth_date, nationality, position, number, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (club_id, full_name, birth_date, nationality, position, int(number), status)
        )
        return f"Играч '{full_name}' беше добавен успешно."
    except Exception as e:
        return f"Грешка при добавяне на играч: {str(e)}"

def get_players_by_club(club_identifier=None):
    """Get all players, optionally filtered by club ID or name"""
    if club_identifier:
        club_id = get_club_id(club_identifier)
        if not club_id:
            return f"Клуб '{club_identifier}' не съществува."
        
        rows = execute_query(
            """SELECT p.*, c.name as club_name 
               FROM players p 
               JOIN clubs c ON p.club_id = c.id 
               WHERE p.club_id = ? 
               ORDER BY p.number""",
            (club_id,),
            fetch=True
        )
    else:
        rows = execute_query(
            """SELECT p.*, c.name as club_name 
               FROM players p 
               JOIN clubs c ON p.club_id = c.id 
               ORDER BY c.name, p.number""",
            fetch=True
        )
    
    if not rows:
        return "Няма намерени играчи."
    
    result = []
    for row in rows:
        result.append(
            f"ID: {row['id']} | {row['full_name']} | {row['club_name']} | "
            f"{row['position']} | #{row['number']} | {row['nationality']} | {row['birth_date']} | {row['status']}"
        )
    return "\n".join(result)

def update_player_position(player_identifier, new_position):
    """Update player's position"""
    if not validate_position(new_position):
        return "Невалидна позиция. Използвайте една от: GK, DF, MF, FW."
    
    player_id = get_player_id(player_identifier)
    if not player_id:
        return f"Играч '{player_identifier}' не съществува."
    
    try:
        execute_query(
            "UPDATE players SET position = ? WHERE id = ?",
            (new_position, player_id)
        )
        return f"Позицията на играч с ID {player_id} беше обновена на {new_position}."
    except Exception as e:
        return f"Грешка при обновяване: {str(e)}"

def update_player_number(player_identifier, new_number):
    """Update player's jersey number"""
    if not validate_number(new_number):
        return "Невалиден номер. Номерът трябва да бъде между 1 и 99."
    
    player_id = get_player_id(player_identifier)
    if not player_id:
        return f"Играч '{player_identifier}' не съществува."
    
    try:
        execute_query(
            "UPDATE players SET number = ? WHERE id = ?",
            (int(new_number), player_id)
        )
        return f"Номерът на играч с ID {player_id} беше сменен на {new_number}."
    except Exception as e:
        return f"Грешка при обновяване: {str(e)}"

def update_player_status(player_identifier, new_status):
    """Update player's status"""
    if not new_status or new_status.strip() == "":
        return "Статусът не може да бъде празен."
    
    player_id = get_player_id(player_identifier)
    if not player_id:
        return f"Играч '{player_identifier}' не съществува."
    
    try:
        execute_query(
            "UPDATE players SET status = ? WHERE id = ?",
            (new_status, player_id)
        )
        return f"Статусът на играч с ID {player_id} беше обновен на '{new_status}'."
    except Exception as e:
        return f"Грешка при обновяване: {str(e)}"

def delete_player(player_identifier):
    """Delete a player by ID or full_name"""
    player_id = get_player_id(player_identifier)
    if not player_id:
        return f"Играч '{player_identifier}' не съществува."
    
    try:
        execute_query(
            "DELETE FROM players WHERE id = ?",
            (player_id,)
        )
        return f"Играч с ID {player_id} беше изтрит."
    except Exception as e:
        return f"Грешка при изтриване: {str(e)}"
