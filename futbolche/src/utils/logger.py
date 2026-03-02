from datetime import datetime
import os


LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'commands.log')


def log_command(user_input: str, result: str) -> None:
    """Append a timestamped command entry to `commands.log`.

    This is intentionally simple; consumers should call this from `main`.
    """
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.utcnow().isoformat()}Z | {user_input} | {result}\n")
    except Exception:
        # Best effort logging; do not raise on logging failure
        pass
