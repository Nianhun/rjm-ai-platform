import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
JAVA_ROOT = ROOT / "apps" / "java-admin-service"


class JavaManagementSkeletonTest(unittest.TestCase):
    def test_spring_boot_skeleton_files_exist(self):
        expected = [
            "pom.xml",
            "src/main/java/com/rjm/formulaai/management/ManagementApplication.java",
            "src/main/java/com/rjm/formulaai/management/controller/FormulaController.java",
            "src/main/java/com/rjm/formulaai/management/controller/ExperimentController.java",
            "src/main/java/com/rjm/formulaai/management/controller/ProcurementController.java",
            "src/main/java/com/rjm/formulaai/management/controller/ReportController.java",
            "src/main/java/com/rjm/formulaai/management/controller/KnowledgeController.java",
            "src/main/java/com/rjm/formulaai/management/client/PythonFormulaAiClient.java",
            "src/main/java/com/rjm/formulaai/management/client/PythonFormulaAiClientConfig.java",
            "src/main/java/com/rjm/formulaai/management/client/PythonFormulaAiProperties.java",
            "src/main/java/com/rjm/formulaai/management/service/FormulaAiManagementService.java",
            "src/main/java/com/rjm/formulaai/management/service/InMemoryFormulaAiManagementService.java",
            "src/main/java/com/rjm/formulaai/management/service/PythonDelegatingFormulaAiManagementService.java",
            "src/main/java/com/rjm/formulaai/management/dto/FormulaRequest.java",
            "src/main/java/com/rjm/formulaai/management/dto/FormulaCandidate.java",
            "src/main/java/com/rjm/formulaai/management/dto/KnowledgeStatusResponse.java",
            "src/main/resources/application.yml",
            "src/test/java/com/rjm/formulaai/management/ManagementApplicationTests.java",
            "src/test/java/com/rjm/formulaai/management/ManagementApiMockMvcTests.java",
            "src/test/java/com/rjm/formulaai/management/JavaPythonIntegrationSmokeTests.java",
            "src/test/java/com/rjm/formulaai/management/client/PythonFormulaAiClientTests.java",
            "src/test/java/com/rjm/formulaai/management/service/PythonDelegatingFormulaAiManagementServiceTests.java",
        ]

        for relative in expected:
            self.assertTrue((JAVA_ROOT / relative).exists(), relative)

    def test_skeleton_uses_java_8_compatible_source(self):
        source_files = list((JAVA_ROOT / "src").rglob("*.java"))
        self.assertGreater(len(source_files), 0)
        combined = "\n".join(path.read_text(encoding="utf-8") for path in source_files)

        self.assertIsNone(re.search(r"\brecord\s+\w+\s*\(", combined))
        self.assertNotIn("var ", combined)
        self.assertIn("@SpringBootApplication", combined)
        self.assertIn("@RestController", combined)
        self.assertIn("PythonFormulaAiClient", combined)
        self.assertIn("PythonDelegatingFormulaAiManagementService", combined)
        self.assertIn("FormulaAIService.recommend", (JAVA_ROOT / "README.md").read_text(encoding="utf-8"))
        smoke_script = ROOT / "scripts" / "integration" / "run_java_python_integration_smoke.ps1"
        self.assertTrue(smoke_script.exists())
        smoke_script_text = smoke_script.read_text(encoding="utf-8")
        self.assertIn("UseYuxiKnowledge", smoke_script_text)
        self.assertIn("RJM_INGREDIENTS_PATH", smoke_script_text)
        self.assertIn("RJM_RELATIONS_PATH", smoke_script_text)
        self.assertIn("run_java_python_integration_smoke.ps1", (JAVA_ROOT / "README.md").read_text(encoding="utf-8"))
        config = (JAVA_ROOT / "src/main/resources/application.yml").read_text(encoding="utf-8")
        self.assertIn("property-naming-strategy: SNAKE_CASE", config)
        self.assertIn("mode: mock", config)


if __name__ == "__main__":
    unittest.main()

