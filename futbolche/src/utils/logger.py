from datetime import datetime, timezone
import os


LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'commands.log')


def log_command(raw_input: str, intent: str, status: str, reason: str = "", affected_ids: dict = None) -> None:
    """Append a structured command entry to `commands.log`.

    Format:
    DateTime       | Intent        | Status | Raw              | Reason         | IDs
    2025-01-01Z    | add_goal      | OK     | Гол Иван 23 мин  |                | match=5,player=12
    2025-01-01Z    | save_result   | ERROR  | Резултат ...      | Duplicate score | match=5
    """
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ids_str = ""
        if affected_ids:
            ids_str = ",".join(f"{k}={v}" for k, v in affected_ids.items())
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {intent:<15} | {status:<5} | {raw_input} | {reason} | {ids_str}\n")
    except Exception:
        pass
