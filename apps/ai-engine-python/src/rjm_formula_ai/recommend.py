from .models import FormulaRequest, Ingredient, IngredientRelation


def _goal_match_score(goal: str, ingredient: Ingredient) -> float:
    return 1.0 if goal in ingredient.functions else 0.35


def _relation_bonus(ingredient_ids: set[str], relations: list[IngredientRelation]) -> float:
    bonus = 0.0
    for relation in relations:
        if relation.source_ingredient_id in ingredient_ids and relation.target_ingredient_id in ingredient_ids:
            if relation.relation_type in {"synergy", "enhance"}:
                bonus += relation.strength + relation.feedback_weight
            if relation.relation_type in {"conflict", "risk"}:
                bonus -= relation.strength
    return bonus


def recommend_formulas(
    request: FormulaRequest,
    ingredients: list[Ingredient],
    relations: list[IngredientRelation],
    limit: int = 3,
) -> list[dict]:
    ranked = sorted(
        ingredients,
        key=lambda item: (_goal_match_score(request.goal, item), item.usage_range.typical_percent),
        reverse=True,
    )
    base_pool = ranked[: max(4, min(len(ranked), 6))]
    formulas: list[dict] = []

    windows = [
        base_pool[:3],
        base_pool[1:4],
        [base_pool[0], base_pool[2], base_pool[3]] if len(base_pool) >= 4 else base_pool[:3],
    ]

    for index, selected in enumerate(windows[:limit], start=1):
        ids = {item.id for item in selected}
        efficacy = sum(_goal_match_score(request.goal, item) for item in selected) / len(selected)
        relation = _relation_bonus(ids, relations)
        skin_feel_penalty = 0.08 if any("粘" in tag for item in selected for tag in item.risk_tags) else 0.0
        overall = max(0.0, min(1.0, 0.55 * efficacy + 0.20 * relation + 0.20 - skin_feel_penalty))

        formulas.append(
            {
                "id": f"FORM-MOIST-{index:03d}",
                "request_id": request.id,
                "goal": request.goal,
                "ingredients": [
                    {
                        "ingredient_id": item.id,
                        "name": item.name_cn or item.name_en or item.inci_name or item.id,
                        "name_cn": item.name_cn,
                        "name_en": item.name_en,
                        "inci_name": item.inci_name,
                        "category": item.category,
                        "evidence_ids": list(item.evidence_ids),
                        "role": "功效/辅助原料",
                        "suggested_percent_min": item.usage_range.min_percent,
                        "suggested_percent_max": item.usage_range.typical_percent,
                    }
                    for item in selected
                ],
                "recommendation_reason": "基于功效匹配、原料协同关系、风险标签和基础用量范围生成。",
                "risk_notes": [tag for item in selected for tag in item.risk_tags],
                "evidence_ids": sorted({eid for item in selected for eid in item.evidence_ids}),
                "score": {
                    "efficacy": round(efficacy, 3),
                    "stability": 0.7,
                    "skin_feel": round(0.8 - skin_feel_penalty, 3),
                    "cost": 0.75,
                    "supply": 0.75,
                    "overall": round(overall, 3),
                },
                "status": "ai_recommended",
            }
        )

    return sorted(formulas, key=lambda item: item["score"]["overall"], reverse=True)
