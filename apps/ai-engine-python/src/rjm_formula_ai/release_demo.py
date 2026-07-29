import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .workflow_smoke import run_smoke_workflow


def run_release_demo(project_root: Path, output_path: Path | None = None, persist: bool = False) -> dict[str, Any]:
    if persist:
        workflow = run_smoke_workflow(project_root)
    else:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workflow = run_smoke_workflow(
                project_root,
                feedback_path=tmp_path / "feedback_events.jsonl",
                screening_path=tmp_path / "screening_events.jsonl",
            )

    summary = _build_summary(workflow)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def _build_summary(workflow: dict[str, Any]) -> dict[str, Any]:
    impact_rows = workflow["impact_report"]["rows"]
    procurement_items = workflow["procurement"]["items"]
    return {
        "release": "initial-demo",
        "scenario": "formula closed-loop release demo",
        "workflow": workflow,
        "demo_steps": [
            "Collect formula request.",
            "Generate AI candidate formula list.",
            "Record engineer screening decision.",
            "Record passing experiment feedback.",
            "Generate feedback impact and learning result.",
            "Generate supplier procurement recommendation by formula ingredients.",
        ],
        "acceptance": {
            "recommended_formula_count": len(impact_rows),
            "engineer_screening_recorded": workflow["screening"]["decision"] in {"keep", "reject", "modify"},
            "experiment_feedback_recorded": workflow["feedback"]["result"] in {"pass", "fail", "partial"},
            "learning_delta_detected": any(abs(row["score_delta"]) > 0 for row in impact_rows),
            "procurement_items_available": len(procurement_items) > 0,
        },
        "capabilities": {
            "current_capabilities": [
                "Recommend candidate formulas from ingredient properties, relation graph, and historical feedback.",
                "Record engineer screening, experiment feedback, impact reports, and procurement recommendations.",
                "Keep candidate formula, evidence, risk, score, and supplier matching data traceable.",
            ]
        },
        "limitations": {
            "current_limitations": [
                "Does not replace formula engineers, lab validation, regulatory compliance, or safety review.",
                "Does not treat Yuxi product co-occurrence as lab-validated synergy.",
                "Does not publish formula ratios, supplier prices, or experiment conclusions without access controls.",
            ]
        },
        "next_steps": {
            "real_data_pilot": [
                "Complete real ingredient, supplier SKU, COA/MSDS, price, and inventory fields.",
                "Continuously backfill experiment batches, screening opinions, and stability metrics.",
                "Calibrate learned_weight and exploration strategies with more pass/fail samples.",
            ]
        },
    }


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RJM initial release acceptance demo.")
    parser.add_argument(
        "--output",
        default=str(_project_root() / "data" / "outputs" / "release_demo_summary.json"),
        help="Path to write the release demo acceptance summary JSON.",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Write demo feedback and screening records to data/runtime instead of temporary logs.",
    )
    args = parser.parse_args()

    summary = run_release_demo(_project_root(), output_path=Path(args.output), persist=args.persist)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
