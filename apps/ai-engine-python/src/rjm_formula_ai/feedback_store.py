import json
from pathlib import Path
from typing import Any


class FeedbackStore:
    def __init__(self, path: Path):
        self.path = path

    def append(self, event: dict[str, Any]) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
        return len(self.read_all())

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    events.append(json.loads(stripped))
        return events
