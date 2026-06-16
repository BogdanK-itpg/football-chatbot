import re
import json
import os
from enum import Enum, auto
from typing import List, Optional, Dict


class ParamType(Enum):
    TEXT = auto()
    INTEGER = auto()
    FLOAT = auto()
    ENUM = auto()
    BOOLEAN = auto()
    DATE = auto()
    SEASON = auto()


class ParameterDef:
    def __init__(self, name: str, param_type: ParamType = ParamType.TEXT,
                 enum_values: Optional[List[str]] = None,
                 required: bool = True, description: str = "",
                 hint: str = ""):
        self.name = name
        self.param_type = param_type
        self.enum_values = enum_values or []
        self.required = required
        self.description = description or name.replace("_", " ").title()
        self.hint = hint

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.param_type.name,
            "enum_values": self.enum_values,
            "required": self.required,
            "description": self.description,
            "hint": self.hint,
        }


class IntentSchema:
    def __init__(self, tag: str, label: str, parameters: List[ParameterDef],
                 description: str = "", example: str = "", category: str = ""):
        self.tag = tag
        self.label = label
        self.parameters = parameters
        self.description = description
        self.example = example
        self.category = category

    def to_dict(self):
        return {
            "tag": self.tag,
            "label": self.label,
            "parameters": [p.to_dict() for p in self.parameters],
            "description": self.description,
            "example": self.example,
            "category": self.category,
        }


_KNOWN_ENUMS = {
    "position": ["GK", "DF", "MF", "FW"],
    "card_type": ["Y", "R"],
    "event_type": ["goal", "assist", "yellow", "red", "appearance"],
    "status": ["активен", "контузен", "наказан", "свободен"],
}

_PARAM_TYPE_RULES = [
    (re.compile(r"position", re.I), ParamType.ENUM),
    (re.compile(r"card_type", re.I), ParamType.ENUM),
    (re.compile(r"event_type", re.I), ParamType.ENUM),
    (re.compile(r"status", re.I), ParamType.ENUM),
    (re.compile(r"^(home_|away_)?goals?$", re.I), ParamType.INTEGER),
    (re.compile(r"minute", re.I), ParamType.INTEGER),
    (re.compile(r"round_no", re.I), ParamType.INTEGER),
    (re.compile(r"(?<!birth_|match_)date$", re.I), ParamType.DATE),
    (re.compile(r"birth_date", re.I), ParamType.DATE),
    (re.compile(r"match_date", re.I), ParamType.DATE),
    (re.compile(r"transfer_date", re.I), ParamType.DATE),
    (re.compile(r"season", re.I), ParamType.SEASON),
    (re.compile(r"fee", re.I), ParamType.FLOAT),
    (re.compile(r"number$", re.I), ParamType.INTEGER),
    (re.compile(r"new_number", re.I), ParamType.INTEGER),
]


def infer_param_type(param_name: str) -> ParamType:
    for pattern, ptype in _PARAM_TYPE_RULES:
        if pattern.search(param_name):
            return ptype
    return ParamType.TEXT


def _extract_params_from_patterns(patterns: List[str]) -> Dict[str, bool]:
    params = {}
    placeholder_re = re.compile(r"\[(\w+)\]")
    for pattern in patterns:
        for match in placeholder_re.finditer(pattern):
            name = match.group(1)
            if name:
                params[name] = True
    return params


def _generate_param_hint(param_name: str) -> str:
    hints = {
        "club_name": "Име на клуба",
        "club_identifier": "Име или ID на клуб",
        "player_identifier": "Име или ID на играч",
        "full_name": "Пълно име на играча",
        "new_name": "Ново име",
        "new_position": "Нова позиция (GK, DF, MF, FW)",
        "new_number": "Нов номер (1-99)",
        "new_status": "Нов статус",
        "league_name": "Име на лигата",
        "league_identifier": "Име или ID на лига",
        "home_team": "Име на домакин",
        "away_team": "Име на гост",
        "home_goals": "Голове на домакин",
        "away_goals": "Голове на гост",
        "match_id": "ID на мач",
        "match_date": "Дата (YYYY-MM-DD)",
        "birth_date": "Дата на раждане (YYYY-MM-DD)",
        "transfer_date": "Дата на трансфер (YYYY-MM-DD)",
        "season": "Сезон (напр. 2025, 2025/26)",
        "card_type": "Тип картон: Y (жълт) или R (червен)",
        "event_type": "Тип събитие",
        "position": "Позиция: GK, DF, MF, FW",
        "number": "Номер на играч (1-99)",
        "minute": "Минута (1-120)",
        "fee": "Трансферна сума",
        "status": "Статус на играч",
        "nationality": "Националност",
        "from_club": "Текущ клуб (или 'няма' за свободен агент)",
        "to_club_identifier": "Клуб, в който се трансферира",
        "player_name": "Име на играч",
        "team_name": "Име на отбор",
        "round_no": "Номер на кръг",
        "league": "Име на лига",
    }
    return hints.get(param_name, f"Въведете {param_name.replace('_', ' ')}")


def _intent_tag_to_label(tag: str) -> str:
    LABEL_MAP = {
        "help": "Помощ",
        "exit": "Изход",
        "create_league": "Създай лига",
        "add_club_to_league": "Добави клуб в лига",
        "remove_club_from_league": "Премахни клуб от лига",
        "get_league_teams": "Отбори в лига",
        "generate_round_robin": "Генерирай кръгове",
        "get_standings": "Класиране",
        "get_fixtures": "Мачове в лига",
        "delete_player": "Изтрий играч",
        "list_all_players": "Всички играчи",
        "add_club": "Добави клуб",
        "list_clubs": "Списък клубове",
        "delete_club": "Изтрий клуб",
        "update_club": "Редактирай клуб",
        "add_player": "Добави играч",
        "list_players": "Играчи в клуб",
        "update_player_position": "Смени позиция",
        "update_player_number": "Смени номер",
        "update_player_status": "Смени статус",
        "club_statistics": "Статистика на клуб",
        "player_statistics": "Статистика на играч",
        "player_metrics": "Метрики на играч",
        "show_transfers_club": "Трансфери на клуб",
        "show_transfers_player": "Трансфери на играч",
        "transfer_player": "Трансферирай играч",
        "show_events": "Събития в мач",
        "show_round": "Покажи кръг",
        "record_match": "Запиши мач",
        "show_match": "Покажи мач",
        "predict_match": "Прогноза за мач",
        "record_event": "Запиши събитие",
        "end_match": "Приключи мач",
    }
    return LABEL_MAP.get(tag, tag.replace("_", " ").title())


def _param_is_optional_in_patterns(param_name: str, patterns: List[str]) -> bool:
    present_count = 0
    for pattern in patterns:
        if f"[{param_name}]" in pattern:
            present_count += 1
    return present_count < len(patterns)


def _param_is_optional_for_intent(tag: str, param_name: str, patterns: List[str]) -> bool:
    # Match the actual command behavior rather than relying only on placeholder frequency.
    explicit_optional_params = {
        "add_player": {"club_identifier", "birth_date", "nationality", "position", "number", "status"},
        "record_event": {"event_type", "minute"},
        "show_events": {"match_id"},
        "transfer_player": {"from_club", "to_club_identifier", "club_identifier", "transfer_date", "fee"},
    }
    if param_name in explicit_optional_params.get(tag, set()):
        return True
    return _param_is_optional_in_patterns(param_name, patterns)


def build_intent_schema(intent_dict: dict, category: str = "") -> IntentSchema:
    tag = intent_dict.get("tag", "")
    patterns = intent_dict.get("patterns", [])
    param_names = _extract_params_from_patterns(patterns)

    parameters = []
    for pname in sorted(param_names.keys()):
        ptype = infer_param_type(pname)
        enum_values = _KNOWN_ENUMS.get(pname.lower(), [])
        if not enum_values and ptype == ParamType.ENUM:
            pass
        required = not _param_is_optional_for_intent(tag, pname, patterns)
        hint = _generate_param_hint(pname)
        parameters.append(ParameterDef(
            name=pname,
            param_type=ptype,
            enum_values=enum_values,
            required=required,
            hint=hint,
        ))

    examples = intent_dict.get("examples", [])
    example = examples[0] if examples else ""
    description = intent_dict.get("responses", [""])[0]

    return IntentSchema(
        tag=tag,
        label=_intent_tag_to_label(tag),
        parameters=parameters,
        description=description,
        example=example,
        category=category,
    )
