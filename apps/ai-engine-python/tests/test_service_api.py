import json
import os
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.http_server import FormulaAIHandler, build_service_from_environment, run_server
from rjm_formula_ai.service import FormulaAIService
from rjm_formula_ai.yuxi_graph_client import YuxiGraphClient


ROOT = Path(__file__).resolve().parents[3]


def _restore_env(name: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


class FakeYuxiGateway:
    def __init__(self, fail=False, empty_subgraph=False):
        self.fail = fail
        self.empty_subgraph = empty_subgraph

    def list_graphs(self):
        if self.fail:
            raise RuntimeError("yuxi offline")
        return [{"id": "kb-cosmetic", "name": "鍖栧鍝佸師鏂欑煡璇嗗簱"}]

    def get_graph_stats(self, kb_id):
        if self.fail:
            raise RuntimeError("yuxi offline")
        return {
            "total_chunks": 13323,
            "indexed_chunks": 13323,
            "pending_chunks": 0,
            "entity_count": 41896,
            "relationship_count": 409315,
        }

    def get_subgraph(self, kb_id, keyword, max_depth, max_nodes, exclude_chunk):
        if self.empty_subgraph:
            return {"nodes": [], "edges": []}
        return {
            "nodes": [
                {"id": "ent-glycerin", "type": "Entity", "name": "Glycerin", "properties": {"entity_id": "ent-glycerin", "description": "Humectant moisturizer"}},
                {"id": "ent-panthenol", "type": "Entity", "name": "Panthenol", "properties": {"entity_id": "ent-panthenol", "description": "Barrier moisturizing active"}},
                {"id": "ent-betaine", "type": "Entity", "name": "Betaine", "properties": {"entity_id": "ent-betaine", "description": "Moisturizing humectant"}},
            ],
            "edges": [
                {"id": "rel-1", "source_id": "ent-glycerin", "target_id": "ent-panthenol", "properties": {"relation_type": "synergy"}},
                {"id": "rel-2", "source_id": "ent-panthenol", "target_id": "ent-betaine", "properties": {"relation_type": "synergy"}},
            ],
        }


class FormulaAIServiceTest(unittest.TestCase):
    def test_recommend_returns_formula_candidates(self):
        service = FormulaAIService.from_project_root(ROOT)

        response = service.recommend(
            {
                "id": "REQ-MOIST-API-001",
                "goal": "保湿",
                "dosage_form": "乳液",
                "constraints": {
                    "preferred_skin_feel": "清爽不粘",
                    "blocked_ingredient_ids": []
                }
            }
        )

        self.assertEqual(response["request_id"], "REQ-MOIST-API-001")
        self.assertEqual(len(response["formulas"]), 3)
        self.assertGreater(response["formulas"][0]["score"]["overall"], 0)

    def test_knowledge_status_reports_loaded_source(self):
        service = FormulaAIService.from_project_root(ROOT)

        status = service.knowledge_status()

        self.assertEqual(status["ingredient_count"], 5)
        self.assertEqual(status["relation_count"], 4)
        self.assertIn("ingredients_path", status["source_paths"])
        self.assertIn("DOC", status["evidence_prefix_counts"])

    def test_knowledge_status_reports_online_yuxi_graph_when_configured(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
        )

        status = service.knowledge_status()

        self.assertEqual(status["knowledge_source"], "yuxi_graph_online")
        self.assertEqual(status["yuxi_graph"]["entity_count"], 41896)
        self.assertEqual(status["yuxi_graph"]["relationship_count"], 409315)
        self.assertEqual(status["yuxi_graph"]["total_chunks"], 13323)

    def test_recommend_uses_online_yuxi_graph_candidates_when_configured(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
        )

        response = service.recommend({"id": "REQ-YUXI-ONLINE-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

        self.assertEqual(response["knowledge_source"], "yuxi_graph_online")
        self.assertEqual(response["yuxi_graph"]["entity_count"], 41896)
        self.assertTrue(response["formulas"])
        first_ids = [item["ingredient_id"] for item in response["formulas"][0]["ingredients"]]
        self.assertTrue(any(item.startswith("YUXI-ENT-") for item in first_ids))

    def test_yuxi_graph_failure_falls_back_to_loaded_snapshot(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway(fail=True)),
        )

        status = service.knowledge_status()
        response = service.recommend({"id": "REQ-YUXI-FALLBACK-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

        self.assertEqual(status["knowledge_source"], "snapshot_fallback")
        self.assertFalse(status["yuxi_graph"]["online"])
        self.assertEqual(response["knowledge_source"], "snapshot_fallback")
        self.assertEqual(len(response["formulas"]), 3)

    def test_yuxi_graph_empty_recall_falls_back_to_loaded_snapshot(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway(empty_subgraph=True)),
        )

        response = service.recommend({"id": "REQ-YUXI-EMPTY-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

        self.assertEqual(response["knowledge_source"], "snapshot_fallback")
        self.assertEqual(len(response["formulas"]), 3)

    def test_knowledge_governance_reports_traceability_quality(self):
        service = FormulaAIService.from_project_root(ROOT)

        governance = service.knowledge_governance()

        self.assertEqual(governance["ingredient_count"], 5)
        self.assertEqual(governance["relation_count"], 4)
        self.assertIn("ingredient_profile", governance["evidence_source_type_counts"])
        self.assertIn("synergy", governance["relation_type_counts"])
        self.assertIn("medium", governance["relation_confidence_counts"])
        self.assertIn("missing_evidence_ids", governance)
        self.assertGreaterEqual(governance["warning_count"], 1)
        self.assertTrue(governance["governance_notes"])

    def test_feedback_recommend_changes_at_least_one_score(self):
        service = FormulaAIService.from_project_root(ROOT)
        before = service.recommend({"id": "REQ-MOIST-API-002", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
        after = service.feedback_recommend(
            {
                "request": {"id": "REQ-MOIST-API-002", "goal": "保湿", "dosage_form": "乳液", "constraints": {}},
                "feedback": [
                    {
                        "result": "pass",
                        "ingredient_ids": [
                            item["ingredient_id"]
                            for item in before["formulas"][0]["ingredients"]
                        ]
                    }
                ]
            }
        )

        before_scores = [item["score"]["overall"] for item in before["formulas"]]
        after_scores = [item["score"]["overall"] for item in after["formulas"]]
        self.assertNotEqual(before_scores, after_scores)

    def test_build_service_from_environment_uses_runtime_paths(self):
        with TemporaryDirectory() as tmp:
            old_feedback = os.environ.get("RJM_FEEDBACK_PATH")
            old_screening = os.environ.get("RJM_SCREENING_PATH")
            try:
                os.environ["RJM_FEEDBACK_PATH"] = str(Path(tmp) / "feedback.jsonl")
                os.environ["RJM_SCREENING_PATH"] = str(Path(tmp) / "screening.jsonl")
                service = build_service_from_environment(ROOT)
                service.record_feedback({"result": "pass", "ingredient_ids": ["ING-BETAINE", "ING-PANTHENOL"]})
                service.record_screening({"formula_id": "FORM-ENV-001", "engineer": "qa", "decision": "keep", "reason": "env path", "modified_ingredients": []})

                self.assertTrue((Path(tmp) / "feedback.jsonl").exists())
                self.assertTrue((Path(tmp) / "screening.jsonl").exists())
            finally:
                if old_feedback is None:
                    os.environ.pop("RJM_FEEDBACK_PATH", None)
                else:
                    os.environ["RJM_FEEDBACK_PATH"] = old_feedback
                if old_screening is None:
                    os.environ.pop("RJM_SCREENING_PATH", None)
                else:
                    os.environ["RJM_SCREENING_PATH"] = old_screening

    def test_build_service_from_environment_uses_knowledge_paths(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ingredients_path = tmp_path / "ingredients.json"
            relations_path = tmp_path / "relations.json"
            ingredients_path.write_text(
                json.dumps(
                    [
                        {
                            "id": "ING-YUXI-GLYCERIN",
                            "name_cn": "Glycerin",
                            "name_en": "Glycerin",
                            "inci_name": "GLYCERIN",
                            "category": "humectant",
                            "functions": ["保湿"],
                            "properties": {},
                            "usage_range": {"min_percent": 1.0, "max_percent": 5.0, "typical_percent": 3.0},
                            "regulatory_limits": [],
                            "risk_tags": [],
                            "evidence_ids": ["YUXI-ING-GLYCERIN"],
                        }
                    ]
                ),
                encoding="utf-8",
            )
            relations_path.write_text("[]\n", encoding="utf-8")
            old_ingredients = os.environ.get("RJM_INGREDIENTS_PATH")
            old_relations = os.environ.get("RJM_RELATIONS_PATH")
            try:
                os.environ["RJM_INGREDIENTS_PATH"] = str(ingredients_path)
                os.environ["RJM_RELATIONS_PATH"] = str(relations_path)
                service = build_service_from_environment(ROOT)

                self.assertEqual([item.id for item in service.ingredients], ["ING-YUXI-GLYCERIN"])
                self.assertEqual(service.relations, [])
            finally:
                if old_ingredients is None:
                    os.environ.pop("RJM_INGREDIENTS_PATH", None)
                else:
                    os.environ["RJM_INGREDIENTS_PATH"] = old_ingredients
                if old_relations is None:
                    os.environ.pop("RJM_RELATIONS_PATH", None)
                else:
                    os.environ["RJM_RELATIONS_PATH"] = old_relations

    def test_build_service_from_environment_enables_yuxi_graph_client(self):
        old_enabled = os.environ.get("RJM_YUXI_GRAPH_ENABLED")
        old_base = os.environ.get("RJM_YUXI_API_BASE")
        old_kb_id = os.environ.get("RJM_YUXI_KB_ID")
        try:
            os.environ["RJM_YUXI_GRAPH_ENABLED"] = "true"
            os.environ["RJM_YUXI_API_BASE"] = "http://127.0.0.1:5050"
            os.environ["RJM_YUXI_KB_ID"] = "kb-cosmetic"

            service = build_service_from_environment(ROOT)

            self.assertIsNotNone(service.yuxi_graph_client)
        finally:
            _restore_env("RJM_YUXI_GRAPH_ENABLED", old_enabled)
            _restore_env("RJM_YUXI_API_BASE", old_base)
            _restore_env("RJM_YUXI_KB_ID", old_kb_id)


class FormulaAIHttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FormulaAIHandler.service = FormulaAIService.from_project_root(ROOT)
        cls.server = run_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_http_recommend_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps({"id": "REQ-MOIST-HTTP-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
        conn.request("POST", "/recommend", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["request_id"], "REQ-MOIST-HTTP-001")
        self.assertEqual(len(payload["formulas"]), 3)

    def test_http_knowledge_status_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/knowledge/status")
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["ingredient_count"], 5)
        self.assertEqual(payload["relation_count"], 4)

    def test_http_knowledge_governance_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/knowledge/governance")
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["ingredient_count"], 5)
        self.assertIn("relation_confidence_counts", payload)
        self.assertIn("warnings", payload)

    def test_http_feedback_impact_report_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps({"id": "REQ-REPORT-HTTP-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
        conn.request("POST", "/reports/feedback-impact", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        body = json.dumps({"id": "REQ-REPORT-HTTP-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
        self.assertIn("feedback_count", payload)
        self.assertEqual(len(payload["rows"]), 3)


if __name__ == "__main__":
    unittest.main()

