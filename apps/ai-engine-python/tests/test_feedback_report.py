import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.feedback_report import build_feedback_impact_report
from rjm_formula_ai.service import FormulaAIService


ROOT = Path(__file__).resolve().parents[3]


class FeedbackReportTest(unittest.TestCase):
    def test_report_compares_baseline_and_learned_scores(self):
        with TemporaryDirectory() as tmp:
            service = FormulaAIService.from_project_root(
                ROOT,
                feedback_path=Path(tmp) / "feedback_events.jsonl",
                screening_path=Path(tmp) / "screening_events.jsonl",
            )
            service.record_feedback(
                {
                    "result": "pass",
                    "formula_id": "FORM-MOIST-001",
                    "ingredient_ids": ["ING-BETAINE", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE"],
                }
            )

            report = build_feedback_impact_report(
                service,
                {"id": "REQ-REPORT-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}},
            )

            self.assertEqual(report["request_id"], "REQ-REPORT-001")
            self.assertEqual(report["feedback_count"], 1)
            self.assertEqual(len(report["rows"]), 3)
            top_row = report["rows"][0]
            self.assertIn("formula_id", top_row)
            self.assertIn("baseline_rank", top_row)
            self.assertIn("learned_rank", top_row)
            self.assertIn("score_delta", top_row)
            self.assertGreater(
                sum(abs(row["score_delta"]) for row in report["rows"]),
                0,
            )


if __name__ == "__main__":
    unittest.main()

