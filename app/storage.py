import json
from pathlib import Path
from app.models import SearchResult

HISTORY_FILE = Path("data/history.json")


def save_result(result: SearchResult) -> None:
    history = load_history()
    history[result.timestamp] = result.model_dump()
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False))


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {}
    try:
        return json.loads(HISTORY_FILE.read_text())
    except json.JSONDecodeError:
        return {}