import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.feedback_store import FeedbackStore
from rjm_formula_ai.load_data import load_formula_requests, load_ingredients, load_relations
from rjm_formula_ai.models import FormulaRequest
from rjm_formula_ai.recommend import recommend_formulas
from rjm_formula_ai.service import FormulaAIService
from rjm_formula_ai.strategy import available_strategy_names, select_strategy


ROOT = Path(__file__).resolve().parents[3]


class RecommendationStrategyTest(unittest.TestCase):
    def setUp(self):
        self.ingredients = load_ingredients(ROOT / "data" / "samples" / "ingredients.moisturizing.json")
        self.relations = load_relations(ROOT / "data" / "samples" / "ingredient_relations.moisturizing.json")
        self.request = load_formula_requests(ROOT / "data" / "samples" / "formula_requests.json")[0]

    def test_baseline_strategy_preserves_existing_recommendation_order(self):
        before = recommend_formulas(self.request, self.ingredients, self.relations, limit=3)
        strategy = select_strategy("baseline")

        after = strategy.recommend(self.request, self.ingredients, self.relations, [], limit=3)

        self.assertEqual([item["id"] for item in before], [item["id"] for item in after])
        self.assertEqual([item["score"]["overall"] for item in before], [item["score"]["overall"] for item in after])

    def test_learned_weight_strategy_uses_feedback_events_explicitly(self):
        feedback = [
            {
                "result": "pass",
                "ingredient_ids": ["ING-GLYCERIN", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE"],
            }
        ]
        baseline = select_strategy("baseline").recommend(self.request, self.ingredients, self.relations, [], limit=3)
        learned = select_strategy("learned_weight").recommend(self.request, self.ingredients, self.relations, feedback, limit=3)

        self.assertNotEqual(
            [item["score"]["overall"] for item in baseline],
            [item["score"]["overall"] for item in learned],
        )
        self.assertEqual("learned_weight", learned[0]["strategy"])

    def test_service_selects_strategy_from_constraints(self):
        with TemporaryDirectory() as tmp:
            feedback_store = FeedbackStore(Path(tmp) / "feedback.jsonl")
            service = FormulaAIService.from_project_root(ROOT, feedback_path=feedback_store.path)
            service.record_feedback(
                {
                    "result": "pass",
                    "ingredient_ids": ["ING-GLYCERIN", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE"],
                }
            )

            response = service.recommend(
                {
                    "id": "REQ-STRATEGY-001",
                    "goal": "保湿",
                    "dosage_form": "乳液",
                    "constraints": {"strategy": "learned_weight"},
                }
            )

            self.assertEqual("learned_weight", response["strategy"])
            self.assertEqual("learned_weight", response["formulas"][0]["strategy"])

    def test_unknown_strategy_falls_back_to_baseline(self):
        self.assertEqual("baseline", select_strategy("missing").name)
        self.assertIn("exploration", available_strategy_names())


if __name__ == "__main__":
    unittest.main()

