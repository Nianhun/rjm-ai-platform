from .models import RawMaterialSku


def _score_sku(sku: RawMaterialSku) -> float:
    sample_bonus = 0.15 if sku.sample_status == "available" else 0.0
    lead_time_score = max(0.0, 1.0 - (sku.lead_time_days / 30.0))
    price_score = max(0.0, 1.0 - (float(sku.price.get("amount_per_kg", 0.0)) / 1000.0))
    return round((0.45 * sku.quality_rating) + (0.25 * lead_time_score) + (0.15 * price_score) + sample_bonus, 3)


def recommend_procurement_for_formula(formula: dict, skus: list[RawMaterialSku]) -> dict:
    skus_by_ingredient: dict[str, list[RawMaterialSku]] = {}
    for sku in skus:
        skus_by_ingredient.setdefault(sku.ingredient_id, []).append(sku)

    items = []
    for ingredient in formula.get("ingredients", []):
        ingredient_id = ingredient["ingredient_id"]
        ingredient_skus = sorted(
            skus_by_ingredient.get(ingredient_id, []),
            key=_score_sku,
            reverse=True,
        )
        recommended_skus = [
            {
                "sku_id": sku.id,
                "supplier_id": sku.supplier_id,
                "specification": sku.specification,
                "price": sku.price,
                "moq_kg": sku.moq_kg,
                "lead_time_days": sku.lead_time_days,
                "qualification_files": sku.qualification_files,
                "sample_status": sku.sample_status,
                "quality_rating": sku.quality_rating,
                "procurement_score": _score_sku(sku),
            }
            for sku in ingredient_skus
        ]
        items.append(
            {
                "ingredient_id": ingredient_id,
                "status": "matched" if recommended_skus else "missing_supplier",
                "recommended_skus": recommended_skus,
            }
        )

    items.sort(key=lambda item: 0 if item["status"] == "matched" else 1)
    return {
        "formula_id": formula["id"],
        "items": items,
    }
