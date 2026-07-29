import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.workflow_smoke import run_smoke_workflow


ROOT = Path(__file__).resolve().parents[3]


class WorkflowSmokeTest(unittest.TestCase):
    def test_smoke_workflow_exercises_closed_loop(self):
        with TemporaryDirectory() as tmp:
            summary = run_smoke_workflow(
                ROOT,
                feedback_path=Path(tmp) / "feedback_events.jsonl",
                screening_path=Path(tmp) / "screening_events.jsonl",
            )

            self.assertEqual(summary["request_id"], "REQ-WORKFLOW-SMOKE")
            self.assertEqual(summary["selected_formula_id"], summary["screening"]["formula_id"])
            self.assertEqual(summary["screening"]["decision"], "keep")
            self.assertEqual(summary["feedback"]["result"], "pass")
            self.assertEqual(summary["impact_report"]["feedback_count"], 1)
            self.assertGreater(
                sum(abs(row["score_delta"]) for row in summary["impact_report"]["rows"]),
                0,
            )
            self.assertEqual(summary["procurement"]["formula_id"], summary["selected_formula_id"])
            self.assertGreaterEqual(len(summary["procurement"]["items"]), 1)


if __name__ == "__main__":
    unittest.main()

