"""Runtime state for the chatbot — current selected match."""

from typing import Optional

_current_match_id: Optional[int] = None


def set_current_match(match_id: int) -> None:
    global _current_match_id
    _current_match_id = match_id


def get_current_match() -> Optional[int]:
    return _current_match_id


def clear_current_match() -> None:
    global _current_match_id
    _current_match_id = None
