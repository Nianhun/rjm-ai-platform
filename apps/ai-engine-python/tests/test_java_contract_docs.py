import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class JavaContractDocsTest(unittest.TestCase):
    def test_openapi_contract_defines_management_endpoints(self):
        path = ROOT / "shared" / "api-contracts" / "java-management" / "openapi.json"
        spec = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(spec["openapi"], "3.1.0")
        self.assertIn("/api/formulas/recommend", spec["paths"])
        self.assertIn("/api/formulas/{formulaId}", spec["paths"])
        self.assertIn("/api/formulas/{formulaId}/screenings", spec["paths"])
        self.assertIn("/api/experiments/feedback", spec["paths"])
        self.assertIn("/api/experiments/batches", spec["paths"])
        self.assertIn("/api/procurement/recommend", spec["paths"])
        self.assertIn("/api/procurement/recommendations/{formulaId}", spec["paths"])
        self.assertIn("/api/procurement/recommendations/{formulaId}/{ingredientId}/status", spec["paths"])
        self.assertIn("/api/reports/feedback-impact", spec["paths"])
        self.assertIn("/api/learning/weights", spec["paths"])
        self.assertIn("/api/formulas/{formulaId}/explanation", spec["paths"])
        self.assertIn("/api/knowledge/status", spec["paths"])
        self.assertIn("/api/knowledge/governance", spec["paths"])
        self.assertIn("/api/evidence/{evidenceId}", spec["paths"])
        self.assertIn("FormulaRecommendationResponse", spec["components"]["schemas"])
        self.assertIn("ArchivedFormulaResponse", spec["components"]["schemas"])
        self.assertIn("LearnedWeightResponse", spec["components"]["schemas"])
        self.assertIn("FormulaLearningExplanationResponse", spec["components"]["schemas"])
        self.assertIn("ExperimentBatchRequest", spec["components"]["schemas"])
        self.assertIn("ExperimentBatchResponse", spec["components"]["schemas"])
        self.assertIn("ExperimentBatchListResponse", spec["components"]["schemas"])
        self.assertIn("KnowledgeStatusResponse", spec["components"]["schemas"])
        self.assertIn("KnowledgeGovernanceResponse", spec["components"]["schemas"])
        self.assertIn("EvidenceResponse", spec["components"]["schemas"])
        self.assertIn("strategy", spec["components"]["schemas"]["FormulaRecommendationResponse"]["properties"])
        self.assertIn("knowledge_source", spec["components"]["schemas"]["FormulaRecommendationResponse"]["properties"])
        self.assertIn("yuxi_graph", spec["components"]["schemas"]["FormulaRecommendationResponse"]["properties"])
        self.assertIn("knowledge_source", spec["components"]["schemas"]["KnowledgeStatusResponse"]["properties"])
        self.assertIn("yuxi_graph", spec["components"]["schemas"]["KnowledgeStatusResponse"]["properties"])
        self.assertIn("strategy", spec["components"]["schemas"]["FormulaCandidate"]["properties"])
        self.assertIn("ApiTokenAuth", spec["components"]["securitySchemes"])
        self.assertEqual(spec["components"]["securitySchemes"]["ApiTokenAuth"]["name"], "X-RJM-API-Token")

        archived_path = spec["paths"]["/api/formulas/{formulaId}"]["get"]
        self.assertEqual(archived_path["operationId"], "getArchivedFormula")
        self.assertEqual(
            archived_path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/ArchivedFormulaResponse",
        )

    def test_java_contract_readme_names_python_mapping(self):
        path = ROOT / "shared" / "api-contracts" / "java-management" / "README.md"
        text = path.read_text(encoding="utf-8")

        self.assertIn("Java 管理系统 API 契约", text)
        self.assertIn("FormulaAIService.recommend", text)
        self.assertIn("FormulaAIService.get_archived_formula", text)
        self.assertIn("FormulaAIService.record_feedback", text)
        self.assertIn("FormulaAIService.create_experiment_batch", text)
        self.assertIn("FormulaAIService.list_experiment_batches", text)
        self.assertIn("FormulaAIService.recommend_procurement", text)
        self.assertIn("FormulaAIService.list_procurement_recommendations", text)
        self.assertIn("FormulaAIService.update_procurement_status", text)
        self.assertIn("FormulaAIService.list_learned_weights", text)
        self.assertIn("FormulaAIService.explain_formula_learning", text)
        self.assertIn("FormulaAIService.knowledge_status", text)
        self.assertIn("FormulaAIService.knowledge_governance", text)
        self.assertIn("FormulaAIService.get_evidence", text)
        self.assertIn("constraints.strategy", text)
        self.assertIn("baseline", text)
        self.assertIn("learned_weight", text)
        self.assertIn("exploration", text)
        self.assertIn("yuxi_graph_online", text)
        self.assertIn("X-RJM-API-Token", text)
        self.assertIn("workflow_smoke", text)


if __name__ == "__main__":
    unittest.main()

