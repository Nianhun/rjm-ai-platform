import argparse
import json
from pathlib import Path
from typing import Any

from .models import FormulaRequest
from .service import FormulaAIService


def build_feedback_impact_report(service: FormulaAIService, request_payload: dict[str, Any]) -> dict[str, Any]:
    request = FormulaRequest(
        id=request_payload["id"],
        goal=request_payload["goal"],
        dosage_form=request_payload.get("dosage_form", ""),
        constraints=dict(request_payload.get("constraints", {})),
    )
    baseline = service.feedback_recommend(
        {
            "request": request_payload,
            "feedback": [],
            "strategy": request.constraints.get("strategy") or "knowledge_graph_ai",
        }
    )["formulas"]
    learned = service.feedback_recommend(
        {
            "request": request_payload,
            "feedback": service._feedback_events(),
            "strategy": request.constraints.get("strategy") or "learned_weight",
        }
    )["formulas"]

    baseline_by_id = _index_ranked_formulas(baseline)
    learned_by_id = _index_ranked_formulas(learned)
    formula_ids = sorted(set(baseline_by_id) | set(learned_by_id))

    rows = []
    for formula_id in formula_ids:
        before = baseline_by_id.get(formula_id)
        after = learned_by_id.get(formula_id)
        before_score = before["formula"]["score"]["overall"] if before else None
        after_score = after["formula"]["score"]["overall"] if after else None
        rows.append(
            {
                "formula_id": formula_id,
                "baseline_rank": before["rank"] if before else None,
                "learned_rank": after["rank"] if after else None,
                "baseline_score": before_score,
                "learned_score": after_score,
                "score_delta": round((after_score or 0.0) - (before_score or 0.0), 3),
                "ingredient_ids": _ingredient_ids(after["formula"] if after else before["formula"]),
            }
        )

    rows.sort(key=lambda item: (item["learned_rank"] is None, item["learned_rank"] or 999))
    return {
        "request_id": request.id,
        "goal": request.goal,
        "feedback_count": len(service.feedback_store.read_all()) if service.feedback_store else 0,
        "rows": rows,
    }


def _index_ranked_formulas(formulas: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {formula["id"]: {"rank": rank, "formula": formula} for rank, formula in enumerate(formulas, start=1)}


def _ingredient_ids(formula: dict[str, Any]) -> list[str]:
    return [item["ingredient_id"] for item in formula["ingredients"]]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare formula rankings before and after recorded feedback.")
    parser.add_argument("--goal", default="保湿")
    parser.add_argument("--dosage-form", default="乳液")
    parser.add_argument("--request-id", default="REQ-FEEDBACK-REPORT")
    args = parser.parse_args()

    service = FormulaAIService.from_project_root(_project_root())
    report = build_feedback_impact_report(
        service,
        {
            "id": args.request_id,
            "goal": args.goal,
            "dosage_form": args.dosage_form,
            "constraints": {},
        },
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

