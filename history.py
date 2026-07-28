import json
from pathlib import Path
from typing import Any


def load_history(path: str) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {"last_lowest_price": None, "last_result_hash": None}

    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"last_lowest_price": None, "last_result_hash": None}


def save_history(path: str, data: dict[str, Any]) -> None:
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
