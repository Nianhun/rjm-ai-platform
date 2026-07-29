import json
from pathlib import Path
from typing import Any


class ScreeningStore:
    def __init__(self, path: Path):
        self.path = path

    def append(self, record: dict[str, Any]) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
        return len(self.read_all())

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
        return records

    def read_by_formula(self, formula_id: str) -> list[dict[str, Any]]:
        return [record for record in self.read_all() if record.get("formula_id") == formula_id]
