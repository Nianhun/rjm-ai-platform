import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.release_demo import run_release_demo


ROOT = Path(__file__).resolve().parents[3]


class ReleaseAcceptanceTest(unittest.TestCase):
    def test_release_demo_generates_business_acceptance_summary(self):
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "release_demo_summary.json"

            summary = run_release_demo(ROOT, output_path=output_path)

            self.assertTrue(output_path.exists())
            saved = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["release"], "initial-demo")
            self.assertEqual(saved["release"], "initial-demo")
            self.assertEqual(summary["scenario"], "formula closed-loop release demo")
            self.assertEqual(summary["workflow"]["request_id"], "REQ-WORKFLOW-SMOKE")
            self.assertGreaterEqual(summary["acceptance"]["recommended_formula_count"], 3)
            self.assertEqual(summary["acceptance"]["engineer_screening_recorded"], True)
            self.assertEqual(summary["acceptance"]["experiment_feedback_recorded"], True)
            self.assertEqual(summary["acceptance"]["learning_delta_detected"], True)
            self.assertEqual(summary["acceptance"]["procurement_items_available"], True)
            self.assertIn("current_capabilities", summary["capabilities"])
            self.assertIn("current_limitations", summary["limitations"])
            self.assertIn("real_data_pilot", summary["next_steps"])

    def test_release_acceptance_docs_and_script_exist(self):
        doc = ROOT / "docs" / "business" / "release_acceptance.md"
        script = ROOT / "scripts" / "run_release_demo.ps1"
        readme = ROOT / "README.md"

        self.assertTrue(doc.exists())
        self.assertTrue(script.exists())
        self.assertTrue(readme.exists())

        doc_text = doc.read_text(encoding="utf-8")
        script_text = script.read_text(encoding="utf-8")
        readme_text = readme.read_text(encoding="utf-8")
        self.assertIn("release_demo_summary.json", doc_text)
        self.assertIn("release_demo_summary.json", script_text)
        self.assertIn("rjm_formula_ai.release_demo", script_text)
        self.assertIn("run_release_demo.ps1", readme_text)
        self.assertIn("docs/business/release_acceptance.md", readme_text)

    def test_release_demo_output_copy_is_business_readable(self):
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "release_demo_summary.json"
            run_release_demo(ROOT, output_path=output_path)
            text = output_path.read_text(encoding="utf-8")

            self.assertIn("demo", text)
            self.assertNotIn("smoke-only", text)


if __name__ == "__main__":
    unittest.main()
