import json
import os
from typing import List, Optional, Dict
from .intent_schema import IntentSchema, build_intent_schema, ParameterDef, ParamType


INTENTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chatbot", "intents.json")
CATEGORIES = {
    "Клубове": ["add_club", "list_clubs", "update_club", "delete_club"],
    "Играчи": ["add_player", "list_players", "list_all_players", "update_player_position",
               "update_player_number", "update_player_status", "delete_player",
               "transfer_player", "show_transfers_player", "show_transfers_club"],
    "Статистика": ["club_statistics", "player_statistics", "player_metrics"],
    "Мачове": ["record_match", "show_match", "record_event", "get_fixtures",
               "show_round", "save_result", "add_goal", "add_card",
               "select_match", "show_events", "predict_match"],
    "Лиги": ["create_league", "add_club_to_league", "remove_club_from_league",
             "get_league_teams", "generate_round_robin", "get_standings", "get_fixtures"],
    "Други": ["help", "exit"],
}


class CommandNode:
    def __init__(self, node_id: str, label: str, node_type: str,
                 children: Optional[List["CommandNode"]] = None,
                 metadata: Optional[Dict] = None):
        self.id = node_id
        self.label = label
        self.type = node_type
        self.children = children or []
        self.metadata = metadata or {}
        self.parent: Optional["CommandNode"] = None
        for child in self.children:
            child.parent = self

    def add_child(self, child: "CommandNode"):
        child.parent = self
        self.children.append(child)

    def find(self, node_id: str) -> Optional["CommandNode"]:
        if self.id == node_id:
            return self
        for child in self.children:
            result = child.find(node_id)
            if result:
                return result
        return None

    def path_from_root(self) -> List["CommandNode"]:
        path = []
        node = self
        while node:
            path.insert(0, node)
            node = node.parent
        return path


class CommandTreeBuilder:
    def __init__(self):
        self._intents: List[dict] = []
        self._schemas: Dict[str, IntentSchema] = {}
        self._load_intents()

    def _load_intents(self):
        try:
            with open(INTENTS_PATH, "r", encoding="utf-8") as f:
                self._intents = json.load(f).get("intents", [])
        except Exception:
            self._intents = []

        for intent in self._intents:
            tag = intent.get("tag", "")
            if tag:
                category = self._find_category(tag)
                schema = build_intent_schema(intent, category)
                self._schemas[tag] = schema

    def _find_category(self, tag: str) -> str:
        for cat_name, tags in CATEGORIES.items():
            if tag in tags:
                return cat_name
        return "Други"

    def get_all_schemas(self) -> Dict[str, IntentSchema]:
        return dict(self._schemas)

    def get_schema(self, tag: str) -> Optional[IntentSchema]:
        return self._schemas.get(tag)

    def get_intents_by_category(self) -> Dict[str, List[IntentSchema]]:
        result: Dict[str, List[IntentSchema]] = {}
        for tag, schema in self._schemas.items():
            cat = schema.category
            if cat not in result:
                result[cat] = []
            result[cat].append(schema)
        return result

    def build_tree(self) -> CommandNode:
        root = CommandNode("root", "Команди", "root")

        for cat_name, tags in CATEGORIES.items():
            cat_node = CommandNode(f"cat_{cat_name}", cat_name, "category")
            root.add_child(cat_node)

            for tag in tags:
                schema = self._schemas.get(tag)
                if not schema:
                    continue
                cmd_node = CommandNode(
                    node_id=f"cmd_{tag}",
                    label=schema.label,
                    node_type="command",
                    metadata={"tag": tag, "example": schema.example, "description": schema.description},
                )
                cat_node.add_child(cmd_node)

                if tag in ("help", "exit"):
                    continue

                for param in schema.parameters:
                    param_node = CommandNode(
                        node_id=f"param_{tag}_{param.name}",
                        label=param.hint or param.description,
                        node_type="parameter",
                        metadata={
                            "tag": tag,
                            "param_name": param.name,
                            "param_type": param.param_type.name,
                            "enum_values": param.enum_values,
                            "required": param.required,
                        },
                    )
                    cmd_node.add_child(param_node)

        return root
