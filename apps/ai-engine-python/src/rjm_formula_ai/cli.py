import json
from pathlib import Path

from .feedback import apply_feedback_to_relations
from .load_data import load_formula_requests, load_ingredients, load_relations
from .recommend import recommend_formulas


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    ingredients = load_ingredients(project_root / "data" / "samples" / "ingredients.moisturizing.json")
    relations = load_relations(project_root / "data" / "samples" / "ingredient_relations.moisturizing.json")
    request = load_formula_requests(project_root / "data" / "samples" / "formula_requests.json")[0]

    before = recommend_formulas(request, ingredients, relations, limit=3)
    output_dir = project_root / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "formula_recommendations.before_feedback.json").write_text(
        json.dumps(before, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    feedback_rows = [
        {
            "result": "pass",
            "ingredient_ids": [
                item["ingredient_id"]
                for item in before[0]["ingredients"]
            ],
        }
    ]
    updated_relations = apply_feedback_to_relations(relations, feedback_rows)
    after = recommend_formulas(request, ingredients, updated_relations, limit=3)
    (output_dir / "formula_recommendations.after_feedback.json").write_text(
        json.dumps(after, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Generated formula recommendation demo outputs.")
    print(output_dir / "formula_recommendations.before_feedback.json")
    print(output_dir / "formula_recommendations.after_feedback.json")


if __name__ == "__main__":
    main()

