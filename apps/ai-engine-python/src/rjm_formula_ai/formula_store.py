import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class FormulaStore:
    def __init__(self, path: Path):
        self.path = path

    def append_many(self, request_id: str, goal: str, formulas: list[dict[str, Any]]) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        stored_at = datetime.now(timezone.utc).isoformat()
        with self.path.open("a", encoding="utf-8") as handle:
            for formula in formulas:
                row = {
                    "formula_id": formula["id"],
                    "request_id": request_id,
                    "goal": goal,
                    "stored_at": stored_at,
                    "formula": formula,
                }
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
                handle.write("\n")
        return len(self.read_all())

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    rows.append(json.loads(stripped))
        return rows

    def read_latest_by_formula(self, formula_id: str) -> dict[str, Any] | None:
        for row in reversed(self.read_all()):
            if row.get("formula_id") == formula_id:
                return row
        return None

    def read_by_request(self, request_id: str) -> list[dict[str, Any]]:
        return [row for row in self.read_all() if row.get("request_id") == request_id]
