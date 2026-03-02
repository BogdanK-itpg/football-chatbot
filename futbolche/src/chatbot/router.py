from typing import Optional, Dict
from services.clubs_service import create_club, list_clubs, delete_club, update_club
import services.players_service as players
from .nlu import _load_intents
import services.statistics_service as stats


def handle_intent(intent: str, params: Optional[Dict[str, str]]) -> str:
    """Route intent to the appropriate service and return presentation string."""
    if intent == 'help':
        help_lines = ["Налични команди:"]
        intents = _load_intents()
        for intent_data in intents:
            tag = intent_data.get('tag')
            if not tag or tag == 'unknown':
                continue
            patterns = intent_data.get('examples', [])
            for p in patterns:
                help_lines.append(f"- {p}")
        return "\n".join(help_lines)

    if intent == 'exit':
        return 'exit'

    # --- Clubs ---
    if intent == 'add_club':
        if not params or 'club_name' not in params:
            return "Името не може да бъде празно. Формат: добави клуб [име]"
        return create_club(params['club_name'])

    if intent == 'list_clubs':
        return list_clubs()

    if intent == 'delete_club':
        if not params or 'club_name' not in params:
            return "Укажете име на клуба. Формат: изтрий клуб [име]"
        return delete_club(params['club_name'])

    if intent == 'update_club':
        if not params:
            return "Невалидни параметри."
        old = params.get('club_name') or params.get('club')
        new = params.get('new_name')
        if not old or not new:
            return "Формат: редактирай клуб [старо име] на [ново име]"
        return update_club(old, new_name=new)

    # --- Players ---
    if intent == 'add_player':
        required = ['full_name', 'club_identifier', 'position', 'number', 'nationality', 'birth_date', 'status']
        # Allow shorthand minimal command: full_name and club_identifier
        if not params or 'full_name' not in params or 'club_identifier' not in params:
            return ("Недостатъчни параметри. Формат: добави играч [full_name] в клуб [club_identifier] "
                    "позиция [position] номер [number] националност [nationality] дата на раждане [birth_date] статус [status]")

        club_id = players.get_club_id(params['club_identifier'])
        if not club_id:
            return f"Клуб '{params['club_identifier']}' не съществува."

        return players.add_player(
            club_id,
            params['full_name'],
            params.get('birth_date'),
            params.get('nationality'),
            params.get('position'),
            params.get('number'),
            params.get('status')
        )

    if intent == 'list_players':
        if params and 'club_identifier' in params:
            return players.get_players_by_club(params['club_identifier'])
        return players.get_players_by_club()

    if intent == 'list_all_players':
        return players.get_players_by_club()

    if intent == 'update_player_position':
        if not params or 'player_identifier' not in params or 'new_position' not in params:
            return "Недостатъчни параметри. Формат: смени позиция на [player_identifier] на [new_position]"
        return players.update_player_position(params['player_identifier'], params['new_position'])

    if intent == 'update_player_number':
        if not params or 'player_identifier' not in params or 'new_number' not in params:
            return "Недостатъчни параметри. Формат: смени номер на [player_identifier] на [new_number]"
        return players.update_player_number(params['player_identifier'], params['new_number'])

    if intent == 'update_player_status':
        if not params or 'player_identifier' not in params or 'new_status' not in params:
            return "Недостатъчни параметри. Формат: смени статус на [player_identifier] на [new_status]"
        return players.update_player_status(params['player_identifier'], params['new_status'])

    if intent == 'delete_player':
        if not params or 'player_identifier' not in params:
            return "Укажете играч за изтриване. Формат: изтрий играч [player_identifier]"
        return players.delete_player(params['player_identifier'])

    # Statistics
    if intent == 'club_statistics':
        if not params or 'club_identifier' not in params:
            return "Недостатъчни параметри. Формат: покажи статистика на клуб [club_identifier]"
        stats_res = stats.get_club_statistics(params['club_identifier'])
        if not stats_res:
            return f"Клуб '{params['club_identifier']}' не съществува."
        return (f"Статистика за клуб {params['club_identifier']}:\n"
                f"Игри: {stats_res['played']}, Победи: {stats_res['wins']}, Равни: {stats_res['draws']}, Загуби: {stats_res['losses']},\n"
                f"Голове за: {stats_res['goals_for']}, Голове срещу: {stats_res['goals_against']}, Голова разлика: {stats_res['goal_difference']}, Точки: {stats_res['points']}")

    if intent == 'player_statistics':
        if not params or 'player_identifier' not in params:
            return "Недостатъчни параметри. Формат: покажи статистика на играч [player_identifier]"
        stats_res = stats.get_player_statistics(params['player_identifier'])
        if not stats_res:
            return f"Играч '{params['player_identifier']}' не съществува."
        return (f"Статистика за играч {params['player_identifier']}:\n"
                f"Голове: {stats_res['goals']}, Асистенции: {stats_res['assists']},\n"
                f"Появи: {stats_res['appearances']}, Жълти: {stats_res['yellow_cards']}, Червени: {stats_res['red_cards']}")

    return "Не разбирам командата. Напишете 'помощ'."
