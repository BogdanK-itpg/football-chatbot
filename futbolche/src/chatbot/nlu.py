import json
import os
import re
from typing import Tuple, Optional, Dict


INTENTS_PATH = os.path.join(os.path.dirname(__file__), 'intents.json')


def _load_intents():
    try:
        with open(INTENTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f).get('intents', [])
    except Exception:
        return []


def _pattern_to_regex(pattern: str) -> Tuple[re.Pattern, list]:
    """Convert a pattern with placeholders like [name] into a compiled regex and list of group names."""
    placeholder = r"\[(\w+)\]"
    parts = re.split(placeholder, pattern)
    regex_parts = []
    groups = []
    for i, p in enumerate(parts):
        if i % 2 == 0:
            # text
            escaped = re.escape(p.strip().lower())
            if escaped:
                regex_parts.append(escaped.replace(r'\ ', r'\s+'))
        else:
            name = p
            groups.append(name)
            regex_parts.append(f"(?P<{name}>.+?)")

    regex = r"\s+".join(regex_parts)
    return re.compile(rf"^{regex}$", re.IGNORECASE), groups


def parse_input(user_input: str) -> Tuple[str, Optional[Dict[str, str]]]:
    """Parse input and return (intent_tag, params_dict).

    If no intent found returns ("unknown", None).
    """
    text = user_input.strip()
    intents = _load_intents()

    for intent in intents:
        tag = intent.get('tag')
        for pattern in intent.get('patterns', []):
            regex, groups = _pattern_to_regex(pattern)
            m = regex.match(text.lower())
            if m:
                params = {k: v.strip() for k, v in m.groupdict().items() if v}
                return tag, params if params else None

    return 'unknown', None
