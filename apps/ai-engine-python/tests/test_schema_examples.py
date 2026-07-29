from pathlib import Path

from rjm_formula_ai.load_data import load_ingredients, load_relations


ROOT = Path(__file__).resolve().parents[3]


def test_load_moisturizing_ingredients():
    ingredients = load_ingredients(ROOT / "data" / "samples" / "ingredients.moisturizing.json")
    assert len(ingredients) >= 4
    assert ingredients[0].id.startswith("ING-")
    assert any("保湿" in item.functions for item in ingredients)


def test_load_moisturizing_relations():
    relations = load_relations(ROOT / "data" / "samples" / "ingredient_relations.moisturizing.json")
    assert len(relations) >= 2
    assert relations[0].relation_type in {"synergy", "conflict", "substitute", "risk", "enhance"}
