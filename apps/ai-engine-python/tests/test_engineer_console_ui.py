import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
UI_ROOT = ROOT / "apps" / "engineer-console"


class EngineerConsoleUiTest(unittest.TestCase):
    def test_static_console_files_exist(self):
        for relative in ["index.html", "styles.css", "app.js", "README.md"]:
            self.assertTrue((UI_ROOT / relative).exists(), relative)

    def test_console_targets_management_api_workflow(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("配方工程师工作台", html)
        self.assertIn("/api/knowledge/status", script)
        self.assertIn("/api/knowledge/governance", script)
        self.assertIn("/api/formulas/recommend", script)
        self.assertIn("/api/formulas/${formulaId}/screenings", script)
        self.assertIn("/api/experiments/feedback", script)
        self.assertIn("/api/experiments/batches", script)
        self.assertIn("/api/reports/feedback-impact", script)
        self.assertIn("/api/procurement/recommend", script)
        self.assertIn("/api/procurement/recommendations/${formulaId}", script)
        self.assertIn("/api/procurement/recommendations/${formulaId}/${ingredientId}/status", script)
        self.assertIn("/api/evidence/${evidenceId}", script)
        self.assertIn("/api/learning/weights", script)
        self.assertIn("/api/formulas/${formulaId}/explanation", script)
        self.assertIn('id="loadLearningExplanation"', html)
        self.assertIn('id="loadSavedProcurement"', html)
        self.assertIn('id="requestProcurementSample"', html)
        self.assertIn('id="loadKnowledgeGovernance"', html)
        self.assertIn('id="createExperimentBatch"', html)
        self.assertIn('id="loadExperimentBatches"', html)
        self.assertIn('id="strategy"', html)
        self.assertIn("strategy: els.strategy.value", script)

    def test_console_has_offline_sample_state(self):
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("offlineKnowledgeStatus", script)
        self.assertIn("offlineKnowledgeGovernance", script)
        self.assertIn("offlineRecommendation", script)
        self.assertIn("YUXI", script)

    def test_console_defaults_api_base_to_serving_origin_and_auto_refreshes(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("http://127.0.0.1:8090", html)
        self.assertIn("defaultApiBase", script)
        self.assertIn("window.location.origin", script)
        self.assertIn("refreshKnowledgeStatus();", script)
        self.assertIn("Yuxi graph online", script)
        self.assertIn("Current recommendation ingredients", script)

    def test_console_has_workbench_status_and_selection_summary(self):
        html = (UI_ROOT / "index.html").read_text(encoding="utf-8")
        script = (UI_ROOT / "app.js").read_text(encoding="utf-8")
        styles = (UI_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="operationStatus"', html)
        self.assertIn('id="selectedFormulaSummary"', html)
        self.assertIn("withActionStatus", script)
        self.assertIn("setActionStatus", script)
        self.assertIn("updateSelectedFormulaSummary", script)
        self.assertIn(".operation-status", styles)
        self.assertIn(".formula-summary", styles)

    def test_console_copy_is_not_mojibake(self):
        suspicious_fragments = ["閻", "缁", "閸", "瀹稿弶", "闁"]
        for relative in ["index.html", "app.js", "README.md"]:
            content = (UI_ROOT / relative).read_text(encoding="utf-8")
            for fragment in suspicious_fragments:
                self.assertNotIn(fragment, content, relative)


if __name__ == "__main__":
    unittest.main()
