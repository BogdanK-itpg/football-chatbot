import re
import json
import os
import clubs_service

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
            
            # Determine if this intent expects a parameter
            # Intents that typically have a club name parameter
            needs_param = tag in ['add_club', 'delete_club', 'update_club']
            
            for pattern in patterns:
                # Convert pattern to regex
                regex_pattern = pattern_to_regex(pattern, needs_param)
                _patterns_cache.append((tag, regex_pattern, needs_param))
    
    return _patterns_cache

def pattern_to_regex(pattern, needs_param):
    """Convert a natural language pattern to a regex pattern."""
    # Escape special regex characters but keep spaces
    escaped = re.escape(pattern.lower().strip())
    
    # If pattern ends with a specific word (like a club name example),
    # we need to make that part dynamic to capture any name
    # Look for patterns like "добави клуб Левски" where "Левски" is an example
    
    # Split into words
    words = pattern.lower().strip().split()
    
    # For intents that need parameters, if the pattern has 3+ words and the last word looks like a proper noun (capitalized in original),
    # treat the last part as a parameter capture
    if needs_param and len(words) >= 3:
        # Check if the last word is capitalized in the original (indicating it's an example name)
        original_words = pattern.strip().split()
        if original_words[-1][0].isupper():
            # The last word is an example - make it a capture group
            # Rebuild regex: first part fixed, then capture everything after
            fixed_part = ' '.join(words[:-1])
            return rf"{re.escape(fixed_part)}\s+(?P<club_name>.+)$"
    
    # For patterns that are just examples with a parameter in the middle like "добави клуб Левски"
    # we can also try to make them more flexible
    
    # If the pattern contains "клуб" and ends with a word, try to capture after "клуб"
    if needs_param and 'клуб' in escaped:
        # Split at the escaped "клуб"
        parts = escaped.split(re.escape('клуб'))
        if len(parts) == 2:
            # Pattern is something like "добави\ клуб\ Левски"
            # Make it: "добави\s+клуб\s+(.+)"
            before = parts[0].rstrip(r'\ ')
            after = parts[1].lstrip(r'\ ')
            if after:
                # There's something after клуб - treat as example, replace with capture
                return rf"{before}\s+клуб\s+(?P<club_name>.+)$"
            else:
                # клуб is at the end, need to capture after
                return rf"{before}\s+клуб\s+(?P<club_name>.+)$"
    
    # For patterns without parameters or that don't match the above,
    # create a flexible regex that matches the whole pattern with optional variations
    # Replace escaped spaces with \s+ to allow multiple spaces
    flexible = escaped.replace(r'\ ', r'\s+')
    # Add start and end anchors
    return rf"^{flexible}$"

def parse_input(user_input):
    """Parse user input and return (intent_tag, parameter)"""
    user_input_lower = user_input.lower().strip()
    
    patterns = build_patterns()
    
    for tag, pattern, needs_param in patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            # Check if pattern has a named capture group for parameters
            if needs_param and 'club_name' in match.groupdict():
                param = match.group('club_name').strip()
                return tag, param
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

def handle_intent(intent, param):
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
        if not param or param.strip() == "":
            return "Името не може да бъде празно."
        return clubs_service.add_club(param)
    
    if intent == "list_clubs":
        return clubs_service.get_all_clubs()
    
    if intent == "delete_club":
        if not param or param.strip() == "":
            return "Името не може да бъде празно."
        return clubs_service.delete_club(param)
    
    if intent == "update_club":
        # TODO: Implement update functionality
        return "Функцията за редактиране все още не е реализирана."
    
    return response


