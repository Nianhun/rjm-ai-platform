from pathlib import Path

from rjm_formula_ai.feedback import apply_feedback_to_relations
from rjm_formula_ai.load_data import load_relations


ROOT = Path(__file__).resolve().parents[3]


def test_successful_feedback_increases_relation_weight():
    relations = load_relations(ROOT / "data" / "samples" / "ingredient_relations.moisturizing.json")
    updated = apply_feedback_to_relations(
        relations,
        [{"result": "pass", "ingredient_ids": ["ING-GLYCERIN", "ING-SODIUM-HYALURONATE"]}],
    )
    before = relations[0].feedback_weight
    after = updated[0].feedback_weight
    assert after > before

