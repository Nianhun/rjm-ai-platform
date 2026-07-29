import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class DeploymentSecurityTest(unittest.TestCase):
    def test_env_template_documents_local_only_defaults_and_token_gate(self):
        path = ROOT / ".env.example"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")

        self.assertIn("RJM_HTTP_HOST=127.0.0.1", text)
        self.assertIn("RJM_HTTP_PORT=8000", text)
        self.assertIn("RJM_JAVA_HOST=127.0.0.1", text)
        self.assertIn("RJM_JAVA_PORT=8080", text)
        self.assertIn("RJM_API_TOKEN_ENABLED=false", text)
        self.assertIn("RJM_API_TOKEN=", text)
        self.assertIn("RJM_FORMULA_PATH=data/runtime/local_demo/formula_candidates.jsonl", text)
        self.assertIn("RJM_YUXI_GRAPH_ENABLED=false", text)
        self.assertIn("RJM_YUXI_API_BASE=http://127.0.0.1:5050", text)
        self.assertIn("RJM_YUXI_KB_ID=", text)
        self.assertIn("RJM_YUXI_API_TOKEN=", text)

    def test_prototype_stack_script_exposes_smoke_and_security_parameters(self):
        path = ROOT / "scripts" / "development" / "run_prototype_stack.ps1"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")

        self.assertIn("[switch]$SmokeOnly", text)
        self.assertIn("[switch]$UseYuxiKnowledge", text)
        self.assertIn("[switch]$UseYuxiGraphOnline", text)
        self.assertIn("[string]$YuxiApiBase = \"http://127.0.0.1:5050\"", text)
        self.assertIn("[string]$YuxiKbId = \"\"", text)
        self.assertIn("[string]$YuxiApiToken = \"\"", text)
        self.assertIn("[string]$BindHost = \"127.0.0.1\"", text)
        self.assertIn("[string]$ApiToken", text)
        self.assertIn("RJM_HTTP_HOST", text)
        self.assertIn("rjm.security.api-token.enabled", text)
        self.assertIn("rjm.security.api-token.value", text)
        self.assertIn("health", text)
        self.assertIn("Stop-Process", text)
        self.assertIn("Start-SanitizedProcess", text)
        self.assertIn('SetEnvironmentVariable("PATH", $null, "Process")', text)
        self.assertIn('$pythonCommand = ($pythonEnv -join "; ") + "; &', text)
        self.assertIn("RJM_YUXI_GRAPH_ENABLED", text)
        self.assertIn("RJM_YUXI_API_BASE", text)
        self.assertIn("RJM_YUXI_KB_ID", text)
        self.assertIn("RJM_YUXI_API_TOKEN", text)

    def test_deployment_runbook_records_ports_data_logs_and_access_rules(self):
        path = ROOT / "docs" / "deployment" / "deployment_runbook.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")

        self.assertIn("127.0.0.1", text)
        self.assertIn("8000", text)
        self.assertIn("8080", text)
        self.assertIn("data/runtime/local_demo", text)
        self.assertIn("X-RJM-API-Token", text)
        self.assertIn("Stop-Process", text)


if __name__ == "__main__":
    unittest.main()
