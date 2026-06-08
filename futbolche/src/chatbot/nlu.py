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
    """Convert a pattern with placeholders like [name] into a compiled regex.

    Handles hyphens and colons correctly (e.g. 'резултат [hg]-[ag]').
    """
    placeholder = r"\[(\w+)\]"
    parts = re.split(placeholder, pattern)
    regex_parts = []
    groups = []

    for i, p in enumerate(parts):
        if i % 2 == 0:
            stripped = p.strip().lower()
            if stripped:
                escaped = re.escape(stripped)
                flexible = escaped.replace(r'\ ', r'\s+')
                regex_parts.append(flexible)
        else:
            name = p
            groups.append(name)
            if name == 'season':
                regex_parts.append(r"(?P<season>\d{4}(?:/\d{2,4})?(?:-\d{2,4})?)")
            else:
                regex_parts.append(f"(?P<{name}>.+?)")

    # Build the regex with flexible spacing:
    # - Between word-text and placeholders: require at least one space (\s+)
    # - Around punctuation (hyphens, colons, arrows): allow zero spaces (\s*)
    punctuation_re = re.compile(r'^\\.$')
    result = ""
    for idx, part in enumerate(regex_parts):
        if idx == 0:
            result = part
        else:
            prev_is_placeholder = regex_parts[idx - 1].startswith('(?P<')
            cur_is_placeholder = part.startswith('(?P<')
            prev_is_punct = bool(punctuation_re.match(regex_parts[idx - 1]))
            cur_is_punct = bool(punctuation_re.match(part))

            # Use \s* when adjacent to punctuation, \s+ otherwise
            if prev_is_punct or cur_is_punct:
                result += r"\s*" + part
            else:
                result += r"\s+" + part

    return re.compile(rf"^{result}$", re.IGNORECASE), groups


def parse_input(user_input: str) -> Tuple[str, Optional[Dict[str, str]]]:
    """Parse input and return (intent_tag, params_dict).

    If no intent found returns ("unknown", None).
    """
    text = user_input.strip()
    lower_text = text.lower()
    intents = _load_intents()

    for intent in intents:
        tag = intent.get('tag')
        for pattern in intent.get('patterns', []):
            regex, groups = _pattern_to_regex(pattern)
            m = regex.match(lower_text)
            if m:
                params = {}
                for k, v in m.groupdict().items():
                    if v:
                        start, end = m.span(k)
                        original = text[start:end].strip()
                        params[k] = original
                return tag, params if params else None

    return 'unknown', None
