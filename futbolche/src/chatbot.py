import re
import json
import os
import clubs_service
import players_service

# Load intents from JSON file
INTENTS_FILE = os.path.join(os.path.dirname(__file__), 'intents.json')

def load_intents():
    """Load intents from the JSON file."""
    try:
        with open(INTENTS_FILE, 'r', encoding='utf-8') as f:
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
                                  'update_player_status', 'delete_player']
            
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
            
            if params:
                return tag, params
            return tag, None
    
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
            if intent_data['tag'] not in ['unknown']:
                # Get a sample pattern to show
                patterns = intent_data['patterns']
                if patterns:
                    help_text += f"- {patterns[0]}\n"
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


