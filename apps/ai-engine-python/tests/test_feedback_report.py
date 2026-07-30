import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.feedback_report import build_feedback_impact_report
from rjm_formula_ai.service import FormulaAIService
from rjm_formula_ai.yuxi_graph_client import YuxiGraphClient


ROOT = Path(__file__).resolve().parents[3]


class FakeYuxiGateway:
    def get_graph_stats(self, kb_id):
        return {"entity_count": 2, "relationship_count": 1, "total_chunks": 2, "indexed_chunks": 2}

    def get_subgraph(self, kb_id, keyword, max_depth, max_nodes, exclude_chunk):
        return {
            "nodes": [
                {"id": "ent-a", "type": "Entity", "name": "Ingredient A", "properties": {"label": "Ingredient", "entity_id": "ent-a"}},
                {"id": "ent-b", "type": "Entity", "name": "Ingredient B", "properties": {"label": "Ingredient", "entity_id": "ent-b"}},
            ],
            "edges": [
                {"id": "rel-a-b", "source_id": "ent-a", "target_id": "ent-b", "properties": {"relation_type": "synergy"}},
            ],
        }


class FakeAiAnalyzer:
    def __init__(self):
        self.calls = []

    def recommend(self, request, knowledge, feedback_events, strategy_name, limit=3):
        self.calls.append({"feedback_count": len(feedback_events), "strategy": strategy_name})
        return [
            {
                "id": "AI-YUXI-REPORT-001",
                "request_id": request.id,
                "goal": request.goal,
                "strategy": strategy_name,
                "ingredients": [
                    {
                        "ingredient_id": knowledge.ingredients[0].id,
                        "role": "selected from Yuxi graph",
                        "suggested_percent_min": 0.1,
                        "suggested_percent_max": 1.0,
                    }
                ],
                "recommendation_reason": "AI generated from Yuxi graph context.",
                "risk_notes": [],
                "evidence_ids": list(knowledge.ingredients[0].evidence_ids),
                "score": {
                    "efficacy": 0.8,
                    "stability": 0.7,
                    "skin_feel": 0.7,
                    "cost": 0.6,
                    "supply": 0.6,
                    "overall": 0.7,
                },
                "status": "ai_recommended",
            }
        ]


class FeedbackReportTest(unittest.TestCase):
    def test_report_compares_ai_recommendations_with_and_without_feedback_context(self):
        ai_analyzer = FakeAiAnalyzer()
        with TemporaryDirectory() as tmp:
            service = FormulaAIService.from_project_root(
                ROOT,
                feedback_path=Path(tmp) / "feedback_events.jsonl",
                screening_path=Path(tmp) / "screening_events.jsonl",
                yuxi_graph_client=YuxiGraphClient(FakeYuxiGateway(), kb_id="kb-test"),
                ai_analyzer=ai_analyzer,
            )
            service.record_feedback(
                {
                    "result": "pass",
                    "formula_id": "FORM-MOIST-001",
                    "ingredient_ids": ["ING-BETAINE", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE"],
                }
            )

            report = build_feedback_impact_report(
                service,
                {"id": "REQ-REPORT-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}},
            )

            self.assertEqual(report["request_id"], "REQ-REPORT-001")
            self.assertEqual(report["feedback_count"], 1)
            self.assertEqual(len(report["rows"]), 1)
            top_row = report["rows"][0]
            self.assertIn("formula_id", top_row)
            self.assertIn("baseline_rank", top_row)
            self.assertIn("learned_rank", top_row)
            self.assertIn("score_delta", top_row)
            self.assertEqual(ai_analyzer.calls[0]["feedback_count"], 0)
            self.assertEqual(ai_analyzer.calls[1]["feedback_count"], 1)
            self.assertEqual(ai_analyzer.calls[1]["strategy"], "learned_weight")


if __name__ == "__main__":
    unittest.main()

