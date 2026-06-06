from typing import Optional, Dict
from services.clubs_service import add_club, get_all_clubs, delete_club, update_club
import services.players_service as players
import services.matches_service as matches
from .nlu import _load_intents
import services.statistics_service as stats
import services.transfers_service as transfers
import services.leagues_service as leagues
from handlers.handler_matches import (
    handle_show_round,
    handle_save_result,
    handle_add_goal,
    handle_select_match,
    handle_add_card,
    handle_show_events,
)
from utils.logger import log_command


CATEGORIES = {
    "Клубове": ["add_club", "list_clubs", "update_club", "delete_club"],
    "Играчи": ["add_player", "list_players", "list_all_players", "update_player_position", "update_player_number", "update_player_status", "delete_player", "transfer_player"],
    "Статистика": ["club_statistics", "player_statistics", "player_metrics"],
    "Мачове": ["record_match", "show_match", "record_event", "get_fixtures", "show_round", "save_result", "add_goal", "add_card", "select_match", "show_events"],
    "Лиги": ["create_league", "add_club_to_league", "remove_club_from_league", "get_league_teams", "generate_round_robin", "get_standings", "get_fixtures"],
}


def handle_intent(intent: str, params: Optional[Dict[str, str]], raw_input: str = "") -> str:
    """Route intent to the appropriate handler/service and return presentation string."""
    result = _route(intent, params)
    status = "OK"
    error_keywords = ["грешка", "не съществува", "невалид", "недостатъч", "няма лига", "няма мач"]
    if result and any(kw in result.lower() for kw in error_keywords):
        status = "ERROR"
    log_command(raw_input, intent, status, result)
    return result


def _route(intent: str, params: Optional[Dict[str, str]]) -> str:
    """Route intent without logging (internal)."""
    if intent == 'help':
        help_lines = ["Налични команди:"]
        intents = _load_intents()
        intent_tags = {i.get('tag') for i in intents if i.get('tag')}

        for category, tags in CATEGORIES.items():
            cmds = []
            for tag in tags:
                if tag in intent_tags:
                    for i in intents:
                        if i.get('tag') == tag:
                            examples = i.get('examples', [])
                            if examples:
                                cmds.append(f"- {examples[0]}")
                            break
            if cmds:
                help_lines.append(f"\n{category}:")
                help_lines.extend(cmds)

        help_lines.append("\n\nДруги:")
        help_lines.append("- изход (затвори чатбота)")
        help_lines.append("- помощ (покажи тази помощ)")

        return "\n".join(help_lines)

    if intent == 'exit':
        return 'exit'

    # --- Match commands (new Bulgarian spec) ---
    if intent == 'show_round':
        return handle_show_round(params or {})

    if intent == 'save_result':
        return handle_save_result(params or {})

    if intent == 'add_goal':
        return handle_add_goal(params or {})

    if intent == 'select_match':
        return handle_select_match(params or {})

    if intent == 'add_card':
        return handle_add_card(params or {})

    if intent == 'show_events':
        return handle_show_events(params or {})

    # --- Clubs ---
    if intent == 'add_club':
        if not params or 'club_name' not in params:
            return "Името не може да бъде празно. Формат: добави клуб [име]"
        return add_club(params['club_name'])

    if intent == 'list_clubs':
        return get_all_clubs()

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

    # --- Leagues ---
    if intent == 'create_league':
        if not params or 'league_name' not in params or 'season' not in params:
            return "Недостатъчни параметри. Формат: създай лига [име] сезон [година]"
        return leagues.create_league(params['league_name'], params['season'])

    if intent == 'add_club_to_league':
        if not params or 'club_identifier' not in params or 'league_identifier' not in params:
            return "Недостатъчни параметри. Формат: добави клуб [клуб] в лига [лига]"
        return leagues.add_club_to_league(params['league_identifier'], params['club_identifier'])

    if intent == 'remove_club_from_league':
        if not params or 'club_identifier' not in params or 'league_identifier' not in params:
            return "Формат: премахни отбор [клуб] от лига [лига]"
        return leagues.remove_club_from_league(params['league_identifier'], params['club_identifier'])

    if intent == 'get_league_teams':
        if not params or 'league_identifier' not in params:
            return "Формат: покажи отбори в лига [лига]"
        teams = leagues.get_league_teams(params['league_identifier'])
        if not teams:
            return "Лигата не съществува или няма отбори."
        return "\n".join(f"- {t['name']} (ID: {t['id']})" for t in teams)

    if intent == 'generate_round_robin':
        if not params or 'league_identifier' not in params:
            return "Формат: генерирай кръгове за лига [лига]"
        return leagues.generate_round_robin(params['league_identifier'])

    if intent == 'get_fixtures':
        if not params or 'league_identifier' not in params:
            return "Формат: покажи мачове [лига]"
        return leagues.get_fixtures(params['league_identifier'])

    # --- Players ---
    if intent == 'add_player':
        required = ['full_name', 'club_identifier', 'position', 'number', 'nationality', 'birth_date', 'status']
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

    if intent == 'player_metrics':
        if not params or 'player_identifier' not in params:
            return "Недостатъчни параметри. Формат: покажи метрики на играч [player_identifier]"
        adv = stats.get_player_advanced_metrics(params['player_identifier'])
        if not adv:
            return f"Играч '{params['player_identifier']}' не съществува."
        return (f"Разширени метрики за {params['player_identifier']}:\n"
                f"Мин. (прибл.): {adv['minutes_played']}, Гол/90: {adv['goals_per_90']}, Асист/90: {adv['assists_per_90']}")

    # --- Matches & Events ---
    if intent == 'record_match':
        if not params:
            return "Недостатъчни параметри. Формат: запиши мач [home_team] срещу [away_team] дата [match_date] резултат [home_goals]-[away_goals]"
        return matches.record_match(
            params.get('home_team'),
            params.get('away_team'),
            params.get('match_date'),
            params.get('home_goals'),
            params.get('away_goals'),
            params.get('league')
        )

    if intent == 'show_match':
        if not params or 'match_id' not in params:
            return "Формат: покажи мач [match_id]"
        m = matches.get_match(params['match_id'])
        if not m:
            return "Мачът не е намерен."
        return f"{m['match_date']}: {m['home_name']} {m['home_goals']}-{m['away_goals']} {m['away_name']}"

    if intent == 'record_event':
        if not params or 'match_id' not in params or 'event_type' not in params:
            return "Недостатъчни параметри. Формат: запиши събитие [event_type] [player_identifier] в мач [match_id] минута [minute]"
        return matches.record_event(
            params.get('match_id'),
            params.get('player_identifier'),
            params.get('event_type'),
            params.get('minute')
        )

    if intent == 'get_standings':
        if not params or 'league_identifier' not in params:
            return "Формат: покажи класиране [league_identifier]"
        return leagues.get_standings(params['league_identifier'])

    if intent == 'transfer_player':
        if not params or 'player_identifier' not in params or 'club_identifier' not in params:
            return "Недостатъчни параметри. Формат: трансферирай играч [player_identifier] в клуб [club_identifier]"
        return transfers.transfer_player(params['player_identifier'], params['club_identifier'])

    return "Не разбирам командата. Напишете 'помощ'."
