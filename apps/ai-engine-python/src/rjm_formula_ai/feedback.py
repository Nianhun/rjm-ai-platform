from dataclasses import replace

from .models import IngredientRelation


def apply_feedback_to_relations(
    relations: list[IngredientRelation],
    feedback_rows: list[dict],
) -> list[IngredientRelation]:
    updated = relations
    for feedback in feedback_rows:
        ingredient_ids = set(feedback.get("ingredient_ids", []))
        delta = 0.05 if feedback.get("result") == "pass" else -0.05
        next_rows: list[IngredientRelation] = []
        for relation in updated:
            applies = (
                relation.source_ingredient_id in ingredient_ids
                and relation.target_ingredient_id in ingredient_ids
            )
            if applies:
                next_rows.append(
                    replace(
                        relation,
                        feedback_weight=max(-0.3, min(0.3, relation.feedback_weight + delta)),
                    )
                )
            else:
                next_rows.append(relation)
        updated = next_rows
    return updated
