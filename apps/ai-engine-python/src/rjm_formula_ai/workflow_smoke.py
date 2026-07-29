import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .engineer_client import submit_screening_decision
from .experiment_client import build_feedback_event, submit_experiment_feedback
from .feedback_report import build_feedback_impact_report
from .service import FormulaAIService


def run_smoke_workflow(
    project_root: Path,
    feedback_path: Path | None = None,
    screening_path: Path | None = None,
) -> dict[str, Any]:
    service = FormulaAIService.from_project_root(
        project_root,
        feedback_path=feedback_path,
        screening_path=screening_path,
    )
    request_payload = {
        "id": "REQ-WORKFLOW-SMOKE",
        "goal": "保湿",
        "dosage_form": "乳液",
        "constraints": {},
    }
    recommendations = service.recommend(request_payload)
    selected_formula = recommendations["formulas"][0]
    selected_formula_id = selected_formula["id"]
    selected_ingredient_ids = [item["ingredient_id"] for item in selected_formula["ingredients"]]

    submit_screening_decision(
        service=service,
        formula_id=selected_formula_id,
        decision="keep",
        reason="Demo keep: recommendation rationale, risk, and supply-chain information are complete.",
        engineer="smoke_formula_engineer",
    )
    feedback_event = build_feedback_event(
        formula_id=selected_formula_id,
        batch_no="BATCH-WORKFLOW-SMOKE",
        result="pass",
        ingredient_ids=selected_ingredient_ids,
        metrics={"stability": "pass", "moisturizing_score": 0.86},
        issues=[],
        engineer_conclusion="Demo feedback: pilot test passed and learning weights may be updated.",
        engineer="smoke_lab_engineer",
        created_at="2026-07-28T10:00:00+08:00",
    )
    submit_experiment_feedback(service, feedback_event)
    impact_report = build_feedback_impact_report(service, request_payload)
    procurement = service.recommend_procurement({"formula": selected_formula})

    screening_records = service.list_screening(selected_formula_id)["records"]
    return {
        "request_id": recommendations["request_id"],
        "selected_formula_id": selected_formula_id,
        "screening": screening_records[-1],
        "feedback": feedback_event,
        "impact_report": impact_report,
        "procurement": procurement,
    }


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RJM formula AI closed-loop smoke workflow.")
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Write to data/runtime instead of isolated temporary logs.",
    )
    args = parser.parse_args()

    if args.persist:
        summary = run_smoke_workflow(_project_root())
    else:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            summary = run_smoke_workflow(
                _project_root(),
                feedback_path=tmp_path / "feedback_events.jsonl",
                screening_path=tmp_path / "screening_events.jsonl",
            )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
