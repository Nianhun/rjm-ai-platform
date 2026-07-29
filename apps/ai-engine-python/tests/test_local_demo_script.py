import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "development" / "run_local_demo.ps1"


class LocalDemoScriptTest(unittest.TestCase):
    def test_script_exists_and_documents_runtime_entrypoints(self):
        self.assertTrue(SCRIPT.exists())
        content = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("[switch]$UseYuxiKnowledge", content)
        self.assertIn("[switch]$SmokeOnly", content)
        self.assertIn("[string]$ApiToken", content)
        self.assertIn("run_prototype_stack.ps1", content)
        self.assertIn("PythonPort = $PythonPort", content)
        self.assertIn("JavaPort = $JavaPort", content)
        self.assertIn('$stackArgs["UseYuxiKnowledge"]', content)
        self.assertIn('$stackArgs["SmokeOnly"]', content)
        self.assertIn('$stackArgs["ApiToken"]', content)

    def test_script_uses_separate_stdout_and_stderr_logs(self):
        content = SCRIPT.read_text(encoding="utf-8")
        stack_content = (ROOT / "scripts" / "development" / "run_prototype_stack.ps1").read_text(encoding="utf-8")

        self.assertIn("run_prototype_stack.ps1", content)
        self.assertIn("python-ai.out.log", stack_content)
        self.assertIn("python-ai.err.log", stack_content)
        self.assertIn("java-management.out.log", stack_content)
        self.assertIn("java-management.err.log", stack_content)


if __name__ == "__main__":
    unittest.main()

