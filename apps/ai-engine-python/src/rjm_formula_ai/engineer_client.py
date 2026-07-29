import argparse
import json
from pathlib import Path
from typing import Any

from .service import FormulaAIService


def build_review_rows(recommendations: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for formula in recommendations["formulas"]:
        rows.append(
            {
                "formula_id": formula["id"],
                "overall": formula["score"]["overall"],
                "ingredient_ids": [item["ingredient_id"] for item in formula["ingredients"]],
                "risk_summary": "; ".join(formula.get("risk_notes", [])) or "no obvious risk notes",
                "reason": formula["recommendation_reason"],
            }
        )
    return rows


def submit_screening_decision(
    service: FormulaAIService,
    formula_id: str,
    decision: str,
    reason: str,
    engineer: str,
    modified_ingredients: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return service.record_screening(
        {
            "formula_id": formula_id,
            "engineer": engineer,
            "decision": decision,
            "reason": reason,
            "modified_ingredients": modified_ingredients or [],
        }
    )


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Review RJM formula recommendations and record engineer screening.")
    parser.add_argument("--goal", default="保湿")
    parser.add_argument("--dosage-form", default="乳液")
    parser.add_argument("--engineer", default="formula_engineer")
    parser.add_argument("--formula-id")
    parser.add_argument("--decision", choices=["keep", "reject", "modify"])
    parser.add_argument("--reason")
    args = parser.parse_args()

    service = FormulaAIService.from_project_root(_project_root())
    recommendations = service.recommend(
        {
            "id": f"REQ-CLIENT-{args.goal}",
            "goal": args.goal,
            "dosage_form": args.dosage_form,
            "constraints": {},
        }
    )
    rows = build_review_rows(recommendations)
    print(json.dumps({"review_rows": rows}, ensure_ascii=False, indent=2))

    if args.decision or args.formula_id or args.reason:
        if not (args.decision and args.formula_id and args.reason):
            raise SystemExit("--formula-id, --decision, and --reason must be provided together.")
        result = submit_screening_decision(
            service=service,
            formula_id=args.formula_id,
            decision=args.decision,
            reason=args.reason,
            engineer=args.engineer,
        )
        print(json.dumps({"screening": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
