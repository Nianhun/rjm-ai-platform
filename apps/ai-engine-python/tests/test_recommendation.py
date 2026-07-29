from pathlib import Path

from rjm_formula_ai.load_data import load_formula_requests, load_ingredients, load_relations
from rjm_formula_ai.recommend import recommend_formulas


ROOT = Path(__file__).resolve().parents[3]


def test_recommend_moisturizing_formulas():
    ingredients = load_ingredients(ROOT / "data" / "samples" / "ingredients.moisturizing.json")
    relations = load_relations(ROOT / "data" / "samples" / "ingredient_relations.moisturizing.json")
    request = load_formula_requests(ROOT / "data" / "samples" / "formula_requests.json")[0]

    formulas = recommend_formulas(request, ingredients, relations, limit=3)

    assert len(formulas) == 3
    assert formulas[0]["goal"] == "保湿"
    assert formulas[0]["score"]["overall"] > 0
    assert formulas[0]["ingredients"]
    assert formulas[0]["recommendation_reason"]
    assert formulas[0]["risk_notes"] is not None
