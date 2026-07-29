import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .service import FormulaAIService


def build_feedback_event(
    formula_id: str,
    batch_no: str,
    result: str,
    ingredient_ids: list[str],
    metrics: dict[str, Any] | None = None,
    issues: list[str] | None = None,
    engineer_conclusion: str = "",
    engineer: str = "lab_engineer",
    created_at: str | None = None,
) -> dict[str, Any]:
    timestamp = created_at or datetime.now().astimezone().isoformat(timespec="seconds")
    return {
        "id": f"EXP-{formula_id}-{batch_no}-{timestamp}",
        "formula_id": formula_id,
        "batch_no": batch_no,
        "result": result,
        "ingredient_ids": ingredient_ids,
        "metrics": metrics or {},
        "issues": issues or [],
        "engineer_conclusion": engineer_conclusion,
        "engineer": engineer,
        "created_at": timestamp,
    }


def submit_experiment_feedback(service: FormulaAIService, event: dict[str, Any]) -> dict[str, Any]:
    return service.record_feedback(event)


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_metrics(value: str) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for pair in parse_csv(value):
        if "=" not in pair:
            raise ValueError(f"metric must use key=value format: {pair}")
        key, raw = pair.split("=", 1)
        metrics[key.strip()] = _parse_metric_value(raw.strip())
    return metrics


def _parse_metric_value(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Record RJM lab experiment feedback for formula learning.")
    parser.add_argument("--formula-id", required=True)
    parser.add_argument("--batch-no", required=True)
    parser.add_argument("--result", required=True, choices=["pass", "fail", "partial"])
    parser.add_argument("--ingredient-ids", required=True, help="Comma-separated ingredient ids.")
    parser.add_argument("--metrics", default="", help="Comma-separated key=value pairs.")
    parser.add_argument("--issues", default="", help="Comma-separated issue descriptions.")
    parser.add_argument("--engineer-conclusion", default="")
    parser.add_argument("--engineer", default="lab_engineer")
    args = parser.parse_args()

    service = FormulaAIService.from_project_root(_project_root())
    event = build_feedback_event(
        formula_id=args.formula_id,
        batch_no=args.batch_no,
        result=args.result,
        ingredient_ids=parse_csv(args.ingredient_ids),
        metrics=parse_metrics(args.metrics) if args.metrics else {},
        issues=parse_csv(args.issues),
        engineer_conclusion=args.engineer_conclusion,
        engineer=args.engineer,
    )
    result = submit_experiment_feedback(service, event)
    print(json.dumps({"feedback": result, "event": event}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

