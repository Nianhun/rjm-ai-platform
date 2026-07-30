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
    def __init__(self, fail=False, empty_subgraph=False, empty_goal_only=False):
        self.fail = fail
        self.empty_subgraph = empty_subgraph
        self.empty_goal_only = empty_goal_only
        self.subgraph_keywords = []

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
        self.subgraph_keywords.append(keyword)
        if keyword == "Phenoxyethanol":
            return {
                "nodes": [
                    {"id": "prod-mask", "type": "Entity", "name": "Studio Ready Hot Perfecting Cream", "properties": {"label": "Product", "entity_id": "prod-mask"}},
                    {"id": "ent-phenoxyethanol", "type": "Entity", "name": "Phenoxyethanol", "properties": {"label": "Ingredient", "entity_id": "ent-phenoxyethanol"}},
                ],
                "edges": [
                    {"id": "contains-1", "source_id": "prod-mask", "target_id": "ent-phenoxyethanol", "type": "CONTAINS", "properties": {"relation_type": "CONTAINS"}},
                ],
            }
        if self.empty_goal_only and keyword != "*":
            return {"nodes": [], "edges": []}
        if self.empty_subgraph:
            return {"nodes": [], "edges": []}
        return {
            "nodes": [
                {"id": "ent-glycerin", "type": "Entity", "name": "Glycerin", "properties": {"label": "Ingredient", "entity_id": "ent-glycerin", "description": "Humectant moisturizer"}},
                {"id": "ent-panthenol", "type": "Entity", "name": "Panthenol", "properties": {"label": "Ingredient", "entity_id": "ent-panthenol", "description": "Barrier moisturizing active"}},
                {"id": "ent-betaine", "type": "Entity", "name": "Betaine", "properties": {"label": "Ingredient", "entity_id": "ent-betaine", "description": "Moisturizing humectant"}},
            ],
            "edges": [
                {"id": "rel-1", "source_id": "ent-glycerin", "target_id": "ent-panthenol", "properties": {"relation_type": "synergy"}},
                {"id": "rel-2", "source_id": "ent-panthenol", "target_id": "ent-betaine", "properties": {"relation_type": "synergy"}},
            ],
        }

    def list_entities(self, kb_id, label="Ingredient", limit=100000):
        if self.fail:
            raise RuntimeError("yuxi offline")
        return [
            {"entity_id": "0e2dbaf04e4ebaf378f5866fc0887323", "name": "Water", "label": "Ingredient"},
            {"entity_id": "9e0989ede09e665c91365eeb437a3f98", "name": "Glycerin", "label": "Ingredient"},
            {"entity_id": "dba175d813da6ec2320e668f799557e0", "name": "Phenoxyethanol", "label": "Ingredient"},
        ]


class FakeAiAnalyzer:
    def __init__(self):
        self.calls = []

    def recommend(self, request, knowledge, feedback_events, strategy_name, limit=3):
        self.calls.append(
            {
                "goal": request.goal,
                "ingredient_count": len(knowledge.ingredients),
                "relation_count": len(knowledge.relations),
                "strategy": strategy_name,
                "limit": limit,
            }
        )
        return [
            {
                "id": "AI-YUXI-001",
                "request_id": request.id,
                "goal": request.goal,
                "strategy": strategy_name,
                "ingredients": [
                    {
                        "ingredient_id": knowledge.ingredients[0].id,
                        "role": "humectant selected by AI from Yuxi graph evidence",
                        "suggested_percent_min": 0.2,
                        "suggested_percent_max": 1.0,
                    }
                ],
                "recommendation_reason": "AI analyzed the Yuxi graph recall and selected evidence-backed candidates.",
                "risk_notes": [],
                "evidence_ids": list(knowledge.ingredients[0].evidence_ids),
                "score": {
                    "efficacy": 0.81,
                    "stability": 0.72,
                    "skin_feel": 0.7,
                    "cost": 0.62,
                    "supply": 0.58,
                    "overall": 0.73,
                },
                "status": "ai_recommended",
            }
        ]

    def chat(self, question, knowledge, history=None, context=None):
        self.calls.append(
            {
                "question": question,
                "ingredient_count": len(knowledge.ingredients),
                "relation_count": len(knowledge.relations),
            }
        )
        return {
            "answer": "可以围绕 Glycerin 和 Panthenol 形成保湿舒缓配方。",
            "follow_up_questions": [],
            "ingredient_ids": [item.id for item in knowledge.ingredients[:2]],
            "evidence_ids": list(knowledge.ingredients[0].evidence_ids),
            "formula_ingredients": [],
            "function_groups": [],
            "relation_edges": [],
            "core_path": [],
        }


class FormulaAIServiceTest(unittest.TestCase):
    def test_recommend_requires_yuxi_graph_client_and_ai_analyzer(self):
        service = FormulaAIService.from_project_root(ROOT)

        with self.assertRaisesRegex(RuntimeError, "yuxi_graph_required"):
            service.recommend({
                "id": "REQ-MOIST-API-001",
                "goal": "保湿",
                "dosage_form": "乳液",
                "constraints": {
                    "preferred_skin_feel": "清爽不粘",
                    "blocked_ingredient_ids": []
                }
            })

        service_with_yuxi = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
        )
        with self.assertRaisesRegex(RuntimeError, "ai_provider_required"):
            service_with_yuxi.recommend({"id": "REQ-NO-AI", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

    def test_knowledge_status_does_not_expose_local_snapshot_when_yuxi_is_unavailable(self):
        service = FormulaAIService.from_project_root(ROOT)

        status = service.knowledge_status()

        self.assertEqual(status["knowledge_source"], "yuxi_graph_unavailable")
        self.assertEqual(status["ingredient_count"], 0)
        self.assertEqual(status["relation_count"], 0)
        self.assertEqual(status["source_paths"], {})
        self.assertEqual(status["evidence_prefix_counts"], {})

    def test_knowledge_status_reports_online_yuxi_graph_when_configured(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
        )

        status = service.knowledge_status()

        self.assertEqual(status["knowledge_source"], "yuxi_graph_online")
        self.assertEqual(status["ingredient_count"], 41896)
        self.assertEqual(status["relation_count"], 409315)
        self.assertEqual(status["yuxi_graph"]["entity_count"], 41896)
        self.assertEqual(status["yuxi_graph"]["relationship_count"], 409315)
        self.assertEqual(status["yuxi_graph"]["total_chunks"], 13323)

    def test_yuxi_entity_names_returns_live_graph_mapping(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
        )

        payload = service.yuxi_entity_names()

        self.assertEqual(payload["source"], "yuxi_graph_online")
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["entity_names"]["YUXI-0E2DBAF04E4EBAF378F5866FC0887323"], "Water")

    def test_recommend_uses_online_yuxi_graph_candidates_when_configured(self):
        ai_analyzer = FakeAiAnalyzer()
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
            ai_analyzer=ai_analyzer,
        )

        response = service.recommend({"id": "REQ-YUXI-ONLINE-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

        self.assertEqual(response["knowledge_source"], "yuxi_graph_online")
        self.assertEqual(response["yuxi_graph"]["entity_count"], 41896)
        self.assertEqual(response["formulas"][0]["id"], "AI-YUXI-001")
        self.assertEqual(ai_analyzer.calls[0]["ingredient_count"], 3)
        self.assertEqual(ai_analyzer.calls[0]["relation_count"], 2)
        first_ids = [item["ingredient_id"] for item in response["formulas"][0]["ingredients"]]
        self.assertTrue(any(item.startswith("YUXI-ENT-") for item in first_ids))

    def test_recommend_uses_wildcard_yuxi_graph_recall_when_goal_node_is_missing(self):
        gateway = FakeYuxiGateway(empty_goal_only=True)
        ai_analyzer = FakeAiAnalyzer()
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(gateway),
            ai_analyzer=ai_analyzer,
        )

        response = service.recommend({"id": "REQ-YUXI-WILDCARD-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

        self.assertEqual(gateway.subgraph_keywords, ["保湿", "*"])
        self.assertEqual(response["formulas"][0]["id"], "AI-YUXI-001")
        self.assertEqual(ai_analyzer.calls[0]["relation_count"], 2)

    def test_yuxi_graph_failure_does_not_fall_back_to_loaded_snapshot(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway(fail=True)),
            ai_analyzer=FakeAiAnalyzer(),
        )

        status = service.knowledge_status()

        self.assertEqual(status["knowledge_source"], "yuxi_graph_unavailable")
        self.assertFalse(status["yuxi_graph"]["online"])
        with self.assertRaisesRegex(RuntimeError, "yuxi_graph_required"):
            service.recommend({"id": "REQ-YUXI-FALLBACK-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

    def test_yuxi_graph_empty_recall_does_not_fall_back_to_loaded_snapshot(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway(empty_subgraph=True)),
            ai_analyzer=FakeAiAnalyzer(),
        )

        with self.assertRaisesRegex(RuntimeError, "yuxi_graph_required"):
            service.recommend({"id": "REQ-YUXI-EMPTY-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

    def test_knowledge_governance_reports_traceability_quality(self):
        service = FormulaAIService.from_project_root(ROOT)

        governance = service.knowledge_governance()

        self.assertEqual(governance["ingredient_count"], 0)
        self.assertEqual(governance["relation_count"], 0)
        self.assertEqual(governance["evidence_source_type_counts"], {})
        self.assertEqual(governance["relation_type_counts"], {})
        self.assertEqual(governance["relation_confidence_counts"], {})
        self.assertIn("missing_evidence_ids", governance)
        self.assertGreaterEqual(governance["warning_count"], 1)
        self.assertTrue(governance["governance_notes"])

    def test_feedback_recommend_uses_ai_with_yuxi_graph_and_feedback_context(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
            ai_analyzer=FakeAiAnalyzer(),
        )
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
        self.assertEqual(before_scores, after_scores)
        self.assertEqual(service.ai_analyzer.calls[-1]["strategy"], "learned_weight")

    def test_chat_returns_display_graph_names_and_relation_edges(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
            ai_analyzer=FakeAiAnalyzer(),
        )

        response = service.chat({"id": "CHAT-1", "message": "给我一个保湿配方"})

        labels = [node["label"] for node in response["knowledge_graph"]["nodes"]]
        edge_labels = [edge["label"] for edge in response["knowledge_graph"]["edges"]]
        self.assertIn("Glycerin", labels)
        self.assertIn("Panthenol", labels)
        self.assertIn("synergy", edge_labels)
        self.assertNotIn("Yuxi 召回", edge_labels)

    def test_chat_uses_element_level_graph_when_question_mentions_known_entity(self):
        gateway = FakeYuxiGateway()
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(gateway),
            ai_analyzer=FakeAiAnalyzer(),
        )

        response = service.chat({"id": "CHAT-PHENOXY", "message": "Phenoxyethanol 是什么？"})

        labels = [node["label"] for node in response["knowledge_graph"]["nodes"]]
        edge_labels = [edge["label"] for edge in response["knowledge_graph"]["edges"]]
        self.assertEqual(gateway.subgraph_keywords[-1], "Phenoxyethanol")
        self.assertIn("Phenoxyethanol", labels)
        self.assertIn("Studio Ready Hot Perfecting Cream", labels)
        self.assertIn("CONTAINS", edge_labels)

    def test_element_graph_returns_one_hop_display_graph(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
            ai_analyzer=FakeAiAnalyzer(),
        )

        response = service.element_graph("YUXI-ENT-GLYCERIN")

        self.assertEqual(response["query"], "YUXI-ENT-GLYCERIN")
        self.assertEqual(response["center"]["label"], "Glycerin")
        self.assertEqual(response["stats"]["node_count"], 3)
        self.assertEqual(response["stats"]["edge_count"], 2)
        self.assertEqual(response["edges"][0]["label"], "synergy")
        self.assertFalse(response["stats"]["truncated"])

    def test_element_graph_returns_empty_response_when_yuxi_has_no_node(self):
        service = FormulaAIService.from_project_root(
            ROOT,
            yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway(empty_subgraph=True)),
            ai_analyzer=FakeAiAnalyzer(),
        )

        response = service.element_graph("YUXI-MISSING")

        self.assertEqual(response["query"], "YUXI-MISSING")
        self.assertNotIn("center", response)
        self.assertEqual(response["nodes"], [])
        self.assertEqual(response["stats"]["node_count"], 0)

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

    def test_http_recommend_endpoint_requires_online_yuxi_and_ai(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps({"id": "REQ-MOIST-HTTP-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
        conn.request("POST", "/recommend", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 503)
        self.assertEqual(payload["error"], "yuxi_graph_required")

    def test_http_recommend_endpoint_returns_ai_yuxi_candidates_when_configured(self):
        old_service = FormulaAIHandler.service
        try:
            FormulaAIHandler.service = FormulaAIService.from_project_root(
                ROOT,
                yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
                ai_analyzer=FakeAiAnalyzer(),
            )
            conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
            body = json.dumps({"id": "REQ-MOIST-HTTP-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
            conn.request("POST", "/recommend", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
            response = conn.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            conn.close()

            self.assertEqual(response.status, 200)
            self.assertEqual(payload["request_id"], "REQ-MOIST-HTTP-001")
            self.assertEqual(payload["knowledge_source"], "yuxi_graph_online")
            self.assertEqual(payload["formulas"][0]["id"], "AI-YUXI-001")
        finally:
            FormulaAIHandler.service = old_service

    def test_http_knowledge_status_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/knowledge/status")
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["ingredient_count"], 0)
        self.assertEqual(payload["relation_count"], 0)

    def test_http_yuxi_entity_names_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/knowledge/entity-names")
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["entity_names"], {})

    def test_http_knowledge_status_lazy_service_uses_project_root(self):
        old_service = FormulaAIHandler.service
        server = None
        thread = None
        try:
            FormulaAIHandler.service = None
            server = run_server("127.0.0.1", 0)
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()

            conn = HTTPConnection("127.0.0.1", port, timeout=5)
            conn.request("GET", "/knowledge/status")
            response = conn.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            conn.close()

            self.assertEqual(response.status, 200)
            self.assertIn("source_paths", payload)
        finally:
            if server is not None:
                server.shutdown()
                server.server_close()
            if thread is not None:
                thread.join(timeout=2)
            FormulaAIHandler.service = old_service

    def test_http_knowledge_governance_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/knowledge/governance")
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["ingredient_count"], 0)
        self.assertIn("relation_confidence_counts", payload)
        self.assertIn("warnings", payload)

    def test_http_feedback_impact_report_endpoint(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps({"id": "REQ-REPORT-HTTP-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
        conn.request("POST", "/reports/feedback-impact", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 503)
        self.assertIn("yuxi_graph_required", payload["error"])

    def test_http_element_graph_endpoint_returns_normalized_graph(self):
        old_service = FormulaAIHandler.service
        try:
            FormulaAIHandler.service = FormulaAIService.from_project_root(
                ROOT,
                yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway()),
                ai_analyzer=FakeAiAnalyzer(),
            )
            conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
            conn.request("GET", "/knowledge/elements/YUXI-ENT-GLYCERIN/graph")
            response = conn.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            conn.close()

            self.assertEqual(response.status, 200)
            self.assertEqual(payload["center"]["label"], "Glycerin")
            self.assertEqual(payload["stats"]["edge_count"], 2)
        finally:
            FormulaAIHandler.service = old_service


if __name__ == "__main__":
    unittest.main()

