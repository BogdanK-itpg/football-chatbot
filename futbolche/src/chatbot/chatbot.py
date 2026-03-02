from .nlu import parse_input
from .router import handle_intent as route_intent


def parse_and_handle(user_input: str):
    """Parse user input and return the response string (or 'exit')."""
    intent, params = parse_input(user_input)
    return route_intent(intent, params)


# Backwards-compatible names used by the rest of the project
def parse_input_wrapper(user_input: str):
    intent, params = parse_input(user_input)
    return intent, params


def handle_intent(intent: str, params):
    return route_intent(intent, params)
