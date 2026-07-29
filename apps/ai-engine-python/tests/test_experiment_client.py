import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.experiment_client import (
    build_feedback_event,
    parse_csv,
    parse_metrics,
    submit_experiment_feedback,
)
from rjm_formula_ai.service import FormulaAIService


ROOT = Path(__file__).resolve().parents[3]


class ExperimentClientTest(unittest.TestCase):
    def test_parse_cli_values(self):
        self.assertEqual(parse_csv("ING-GLYCERIN, ING-BETAINE"), ["ING-GLYCERIN", "ING-BETAINE"])
        self.assertEqual(
            parse_metrics("stability=pass,moisturizing_score=0.86,irritation=false"),
            {"stability": "pass", "moisturizing_score": 0.86, "irritation": False},
        )

    def test_parse_metrics_rejects_missing_separator(self):
        with self.assertRaises(ValueError):
            parse_metrics("stability")

    def test_build_feedback_event_structures_lab_result(self):
        event = build_feedback_event(
            formula_id="FORM-MOIST-001",
            batch_no="BATCH-001",
            result="pass",
            ingredient_ids=["ING-GLYCERIN", "ING-BETAINE"],
            metrics={"stability": "pass", "moisturizing_score": 0.86},
            issues=["slightly sticky feel"],
            engineer_conclusion="moisturizing result meets target; recommend retest",
            engineer="lab_engineer",
            created_at="2026-07-28T10:00:00+08:00",
        )

        self.assertTrue(event["id"].startswith("EXP-FORM-MOIST-001-BATCH-001"))
        self.assertEqual(event["result"], "pass")
        self.assertEqual(event["ingredient_ids"], ["ING-GLYCERIN", "ING-BETAINE"])
        self.assertEqual(event["metrics"]["moisturizing_score"], 0.86)
        self.assertEqual(event["issues"], ["slightly sticky feel"])
        self.assertEqual(event["engineer"], "lab_engineer")

    def test_submit_experiment_feedback_records_event(self):
        with TemporaryDirectory() as tmp:
            service = FormulaAIService.from_project_root(
                ROOT,
                feedback_path=Path(tmp) / "feedback_events.jsonl",
                screening_path=Path(tmp) / "screening_events.jsonl",
            )
            event = build_feedback_event(
                formula_id="FORM-MOIST-001",
                batch_no="BATCH-001",
                result="fail",
                ingredient_ids=["ING-GLYCERIN", "ING-BETAINE"],
                metrics={"stability": "fail"},
                issues=["phase separation"],
                engineer_conclusion="stability failed; do not proceed to procurement",
                engineer="lab_engineer",
                created_at="2026-07-28T10:00:00+08:00",
            )

            result = submit_experiment_feedback(service, event)

            events = service.feedback_store.read_all()
            self.assertEqual(result["stored"], True)
            self.assertEqual(events[0]["formula_id"], "FORM-MOIST-001")
            self.assertEqual(events[0]["result"], "fail")


if __name__ == "__main__":
    unittest.main()
