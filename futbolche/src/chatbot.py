import re
import json
import os
from services import clubs_service, players_service, statistics_service

# Load intents from JSON file. Try top-level `src/intents.json` then `src/chatbot/intents.json`.
INTENTS_FILE = os.path.join(os.path.dirname(__file__), 'intents.json')
ALT_INTENTS_FILE = os.path.join(os.path.dirname(__file__), 'chatbot', 'intents.json')

def load_intents():
    """Load intents from the JSON file."""
    try:
        path = INTENTS_FILE
        if not os.path.exists(path) and os.path.exists(ALT_INTENTS_FILE):
            path = ALT_INTENTS_FILE
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('intents', [])
    except Exception as e:
        print(f"Error loading intents: {e}")
        return []

# Cache for intents and their responses
_intents_cache = None
_responses_cache = {}
_patterns_cache = []

def build_patterns():
    """Build regex patterns from intents."""
    global _intents_cache, _responses_cache, _patterns_cache
    
    if _intents_cache is None:
        _intents_cache = load_intents()
        _responses_cache = {}
        _patterns_cache = []
        
        for intent in _intents_cache:
            tag = intent['tag']
            patterns = intent['patterns']
            responses = intent.get('responses', [])
            
            # Cache responses for this intent
            _responses_cache[tag] = responses
            
            # Determine if this intent expects parameters
            needs_param = tag in ['add_club', 'delete_club', 'update_club',
                                  'add_player', 'list_players', 'list_all_players',
                                  'update_player_position', 'update_player_number',
                                  'update_player_status', 'delete_player',
                                  'club_statistics', 'player_statistics']
            
            for pattern in patterns:
                # Convert pattern to regex
                regex_pattern = pattern_to_regex(pattern, needs_param)
                _patterns_cache.append((tag, regex_pattern, needs_param))
    
    return _patterns_cache

def pattern_to_regex(pattern, needs_param):
    """Convert a natural language pattern to a regex pattern with named capture groups."""
    placeholder_pattern = r'\[(\w+)\]'
    parts = re.split(placeholder_pattern, pattern)
    
    if len(parts) == 1:
        # No placeholders
        escaped = re.escape(pattern.lower().strip())
        flexible = escaped.replace(r'\ ', r'\s+')
        return rf"^{flexible}$"
    
    # parts: [text_before, placeholder1, text_after1, placeholder2, ...]
    # Process text parts: strip, escape, replace spaces with \s+
    # Join all parts with \s+ to allow flexible spacing between tokens
    result_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Text part - strip whitespace, escape, and normalize spaces
            stripped = part.strip()
            if stripped:
                escaped = re.escape(stripped.lower())
                flexible = escaped.replace(r'\ ', r'\s+')
                result_parts.append(flexible)
        else:
            # Placeholder - convert to named capture group
            result_parts.append(f'(?P<{part}>.+?)')
    
    # Join with \s+ to require at least one whitespace between elements
    regex = r'\s+'.join(result_parts)
    return rf"^{regex}$"

def parse_input(user_input):
    """Parse user input and return (intent_tag, parameters_dict)"""
    user_input_lower = user_input.lower().strip()
    
    patterns = build_patterns()
    
    for tag, pattern, needs_param in patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            # Extract all named capture groups as a dictionary
            params = {}
            for name, value in match.groupdict().items():
                if value:
                    params[name] = value.strip()

            # If this intent expects structured parameters but the regex
            # capture looks suspicious (e.g. a captured value contains
            # marker words for subsequent parameters), attempt a
            # marker-based fallback parser for more robust extraction.
            def _looks_suspect(pdict):
                if not pdict:
                    return True
                # markers commonly used in player add commands
                markers = ['в клуб', 'на клуб', 'позиция', 'номер', 'националност', 'дата на раждане', 'статус']
                for v in pdict.values():
                    if any(m in v for m in markers):
                        return True
                return False

            if needs_param and tag == 'add_player' and _looks_suspect(params):
                fallback = _extract_add_player_params(user_input_lower)
                if fallback:
                    return tag, fallback

            if params:
                # Normalize common player params when present (regex captures are lowercase)
                if tag == 'add_player':
                    # Position should be uppercase code like GK/DF/MF/FW
                    if 'position' in params and params['position']:
                        params['position'] = params['position'].strip().upper()
                    # Normalize birth_date like 2000-1-1 -> 2000-01-01
                    if 'birth_date' in params and params['birth_date']:
                        bd = params['birth_date'].strip()
                        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", bd)
                        if m:
                            y, mm, dd = m.groups()
                            params['birth_date'] = f"{y}-{int(mm):02d}-{int(dd):02d}"
                    # Trim number
                    if 'number' in params and params['number']:
                        params['number'] = params['number'].strip()
                return tag, params
            return tag, None
    
    # Final heuristic: if no regex matched, but input looks like an add_player command,
    # try the marker-based extractor as a last resort.
    if 'добави играч' in user_input_lower or 'регистрирай играч' in user_input_lower or 'създай играч' in user_input_lower:
        fallback = _extract_add_player_params(user_input_lower)
        if fallback:
            return 'add_player', fallback

    return "unknown", None

def get_random_response(intent_tag):
    """Get a random response for the given intent tag."""
    global _responses_cache
    if intent_tag in _responses_cache:
        responses = _responses_cache[intent_tag]
        if responses:
            import random
            return random.choice(responses)
    return None


def _extract_add_player_params(text: str):
    """Fallback extraction for add_player commands using marker keywords.

    Recognizes: full_name, club_identifier, position, number, nationality,
    birth_date, status. Returns a dict or None.
    """
    markers = {
        'club': ['в клуб', 'на клуб', ' в '],
        # include common misspellings/short forms for position
        'position': ['позиция', 'позоция', 'поз', 'пози'],
        'number': ['номер'],
        'nationality': ['националност'],
        'birth_date': ['дата на раждане', 'дата'],
        'status': ['статус']
    }

    # Helper to find earliest occurrence of any marker from a list
    def find_marker_pos(s, marker_list):
        positions = [(s.find(m), m) for m in marker_list if s.find(m) != -1]
        if not positions:
            return -1, None
        # Choose the earliest occurrence; if tied, prefer the longest marker (more specific)
        positions.sort(key=lambda x: (x[0], -len(x[1])))
        return positions[0]

    # Find start of command after "добави играч" or variants
    start_tokens = ['добави играч', 'регистрирай играч', 'създай играч']
    start_pos = -1
    for tok in start_tokens:
        p = text.find(tok)
        if p != -1:
            start_pos = p + len(tok)
            break
    if start_pos == -1:
        # not an add_player-like start
        return None

    # Build an ordered list of marker positions
    marker_positions = []
    for key, mlist in markers.items():
        pos, m = find_marker_pos(text, mlist)
        if pos != -1:
            marker_positions.append((pos, key, m))

    # Sort by position
    marker_positions.sort(key=lambda x: x[0])

    # Determine slices between markers
    params = {}
    cur = start_pos

    for idx, (pos, key, mtoken) in enumerate(marker_positions):
        # text from cur to pos is the previous param (or full_name for first)
        segment = text[cur:pos].strip()
        if idx == 0:
            # first segment is full_name
            if segment:
                params['full_name'] = segment
        else:
            # For safety, assign nothing for unexpected ordering
            pass

        # Next, find end of this marker's value: either next marker pos or end
        next_pos = marker_positions[idx+1][0] if idx+1 < len(marker_positions) else len(text)
        value = text[pos + len(mtoken):next_pos].strip()
        if key == 'club':
            params['club_identifier'] = value
        elif key == 'position':
            params['position'] = value.split()[0].upper() if value else ''
        elif key == 'number':
            params['number'] = value.split()[0] if value else ''
        elif key == 'nationality':
            params['nationality'] = value
        elif key == 'birth_date':
            bd = value.split()[0] if value else ''
            # Normalize date like 2000-1-1 -> 2000-01-01
            m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", bd)
            if m:
                y, mm, dd = m.groups()
                params['birth_date'] = f"{y}-{int(mm):02d}-{int(dd):02d}"
            else:
                params['birth_date'] = bd
        elif key == 'status':
            params['status'] = value

        cur = next_pos

    # If no markers found, attempt a very rough split by keywords
    if not params:
        # Try a regex fallback that matches common phrasing like:
        # "добави играч <full_name> в <club> позиция <position> номер <number> ..."
        regex = re.compile(
            r"(?:добави играч|регистрирай играч|създай играч)\s+"
            r"(?P<full_name>.+?)\s+в(?:\s+клуб)?\s+"
            r"(?P<club_identifier>.+?)"
            r"(?:\s+позиция\s+(?P<position>\w+))?"
            r"(?:\s+номер\s+(?P<number>\d{1,3}))?"
            r"(?:\s+националност\s+(?P<nationality>[\w\s]+?))?"
            r"(?:\s+дата\s+на\s+раждане\s+(?P<birth_date>\d{4}-\d{1,2}-\d{1,2}))?"
            r"(?:\s+статус\s+(?P<status>[\w\s]+))?\s*$",
            re.IGNORECASE | re.UNICODE,
        )

        m = regex.search(text)
        if not m:
            return None

        gd = m.groupdict()
        # Normalize and assign
        if gd.get('full_name'):
            params['full_name'] = gd['full_name'].strip()
        if gd.get('club_identifier'):
            params['club_identifier'] = gd['club_identifier'].strip()
        if gd.get('position'):
            params['position'] = gd['position'].strip().upper()
        if gd.get('number'):
            params['number'] = gd['number'].strip()
        if gd.get('nationality'):
            params['nationality'] = gd['nationality'].strip()
        if gd.get('birth_date'):
            bd = gd['birth_date'].strip()
            m2 = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", bd)
            if m2:
                y, mm, dd = m2.groups()
                params['birth_date'] = f"{y}-{int(mm):02d}-{int(dd):02d}"
            else:
                params['birth_date'] = bd
        if gd.get('status'):
            params['status'] = gd['status'].strip()

    # Ensure full_name is captured: if not, try from start_pos to first marker
    if 'full_name' not in params:
        first_marker_pos = marker_positions[0][0] if marker_positions else len(text)
        fn = text[start_pos:first_marker_pos].strip()
        if fn:
            params['full_name'] = fn

    return params

def handle_intent(intent, params):
    """Handle the parsed intent and return a response."""
    # Get a response from intents.json
    response = get_random_response(intent)
    if not response:
        response = "Не разбирам командата. Напишете 'помощ'."
    
    if intent == "exit":
        return "exit"
    
    if intent == "help":
        # Build help from all available intents
        help_text = "Налични команди:\n"
        for intent_data in _intents_cache:
            tag = intent_data.get('tag')
            if tag and tag != 'unknown':
                patterns = intent_data.get('patterns', [])
                for p in patterns:
                    help_text += f"- {p}\n"
        return help_text.strip()
    
    if intent == "add_club":
        if not params or 'club_name' not in params:
            return "Името не може да бъде празно."
        return clubs_service.add_club(params['club_name'])
    
    if intent == "list_clubs":
        return clubs_service.get_all_clubs()
    
    if intent == "delete_club":
        if not params or 'club_name' not in params:
            return "Името не може да бъде празно."
        return clubs_service.delete_club(params['club_name'])
    
    if intent == "update_club":
        # TODO: Implement update functionality
        return "Функцията за редактиране все още не е реализирана."
    
    # Player intents
    if intent == "add_player":
        # Required parameters: full_name, club_identifier, position, number, nationality, birth_date, status
        required = ['full_name', 'club_identifier', 'position', 'number', 'nationality', 'birth_date', 'status']
        if not all(param in params for param in required):
            return "Недостатъчни параметри. Използвайте: Добави играч [име] в клуб [клуб] позиция [позиция] номер [номер] националност [националност] дата на раждане [дата] статус [статус]"
        
        club_id = players_service.get_club_id(params['club_identifier'])
        if not club_id:
            return f"Клуб '{params['club_identifier']}' не съществува."
        
        return players_service.add_player(
            club_id,
            params['full_name'],
            params['birth_date'],
            params['nationality'],
            params['position'],
            params['number'],
            params['status']
        )
    
    if intent == "list_players":
        if params and 'club_identifier' in params:
            return players_service.get_players_by_club(params['club_identifier'])
        return players_service.get_players_by_club()
    
    if intent == "list_all_players":
        return players_service.get_players_by_club()

    # Statistics intents
    if intent == "club_statistics":
        if not params or 'club_identifier' not in params:
            return "Недостатъчни параметри. Използвайте: Покажи статистика на клуб [клуб]"
        stats = statistics_service.get_club_statistics(params['club_identifier'])
        if not stats:
            return f"Клуб '{params['club_identifier']}' не съществува."
        return (
            f"Статистика за клуб {params['club_identifier']}:\n"
            f"Игри: {stats['played']}, Победи: {stats['wins']}, Равни: {stats['draws']}, Загуби: {stats['losses']},\n"
            f"Голове за: {stats['goals_for']}, Голове срещу: {stats['goals_against']}, Голова разлика: {stats['goal_difference']}, Точки: {stats['points']}"
        )

    if intent == "player_statistics":
        if not params or 'player_identifier' not in params:
            return "Недостатъчни параметри. Използвайте: Покажи статистика на играч [име/ID]"
        stats = statistics_service.get_player_statistics(params['player_identifier'])
        if not stats:
            return f"Играч '{params['player_identifier']}' не съществува."
        return (
            f"Статистика за играч {params['player_identifier']}:\n"
            f"Голове: {stats['goals']}, Асистенции: {stats['assists']},\n"
            f"Появи: {stats['appearances']}, Жълти: {stats['yellow_cards']}, Червени: {stats['red_cards']}"
        )
    
    if intent == "update_player_position":
        if not params or 'player_identifier' not in params or 'new_position' not in params:
            return "Недостатъчни параметри. Използвайте: Смени позиция на [име/ID] на [позиция]"
        return players_service.update_player_position(params['player_identifier'], params['new_position'])
    
    if intent == "update_player_number":
        if not params or 'player_identifier' not in params or 'new_number' not in params:
            return "Недостатъчни параметри. Използвайте: Смени номер на [име/ID] на [номер]"
        return players_service.update_player_number(params['player_identifier'], params['new_number'])
    
    if intent == "update_player_status":
        if not params or 'player_identifier' not in params or 'new_status' not in params:
            return "Недостатъчни параметри. Използвайте: Смени статус на [име/ID] на [статус]"
        return players_service.update_player_status(params['player_identifier'], params['new_status'])
    
    if intent == "delete_player":
        if not params or 'player_identifier' not in params:
            return "Недостатъчен параметър. Използвайте: Изтрий играч [име/ID]"
        return players_service.delete_player(params['player_identifier'])
    
    return response


