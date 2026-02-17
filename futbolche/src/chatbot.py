import re
import clubs_service

def parse_input(user_input):
    user_input = user_input.lower()

    if re.search(r"\b(помощ|help)\b", user_input):
        return "help", None

    if re.search(r"\b(изход|exit)\b", user_input):
        return "exit", None

    if re.search(r"добави клуб (.+)", user_input):
        match = re.search(r"добави клуб (.+)", user_input)
        return "add_club", match.group(1).strip()

    if re.search(r"(покажи|списък).*(клуб)", user_input):
        return "list_clubs", None

    if re.search(r"изтрий клуб (.+)", user_input):
        match = re.search(r"изтрий клуб (.+)", user_input)
        return "delete_club", match.group(1).strip()

    return "unknown", None


def handle_intent(intent, param):
    if intent == "help":
        return """Налични команди:
- Добави клуб <име>
- Покажи всички клубове
- Изтрий клуб <име>
- помощ
- изход"""

    if intent == "exit":
        return "exit"

    if intent == "add_club":
        return clubs_service.add_club(param)

    if intent == "list_clubs":
        return clubs_service.get_all_clubs()

    if intent == "delete_club":
        return clubs_service.delete_club(param)

    return "Не разбирам командата. Напишете 'помощ'."
