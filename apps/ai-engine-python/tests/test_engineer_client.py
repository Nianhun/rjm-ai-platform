import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.engineer_client import build_review_rows, submit_screening_decision
from rjm_formula_ai.service import FormulaAIService


ROOT = Path(__file__).resolve().parents[3]


class EngineerClientTest(unittest.TestCase):
    def test_build_review_rows_summarizes_formula_candidates(self):
        service = FormulaAIService.from_project_root(ROOT)
        recommendations = service.recommend({"id": "REQ-CLIENT-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

        rows = build_review_rows(recommendations)

        self.assertEqual(len(rows), 3)
        self.assertIn("formula_id", rows[0])
        self.assertIn("overall", rows[0])
        self.assertIn("ingredient_ids", rows[0])
        self.assertIn("risk_summary", rows[0])

    def test_submit_screening_decision_records_keep_reason(self):
        with TemporaryDirectory() as tmp:
            service = FormulaAIService.from_project_root(
                ROOT,
                feedback_path=Path(tmp) / "feedback_events.jsonl",
                screening_path=Path(tmp) / "screening_events.jsonl",
            )

            reason = "moisturizing logic is clear; move to pilot test"
            result = submit_screening_decision(
                service=service,
                formula_id="FORM-MOIST-001",
                decision="keep",
                reason=reason,
                engineer="formula_engineer",
            )
            records = service.list_screening("FORM-MOIST-001")

            self.assertEqual(result["stored"], True)
            self.assertEqual(records["records"][0]["decision"], "keep")
            self.assertEqual(records["records"][0]["reason"], reason)


if __name__ == "__main__":
    unittest.main()
