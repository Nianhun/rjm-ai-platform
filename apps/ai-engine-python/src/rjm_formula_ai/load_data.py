import json
from pathlib import Path
from typing import Any

from .models import FormulaRequest, Ingredient, IngredientRelation, RawMaterialSku, UsageRange


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_ingredients(path: Path) -> list[Ingredient]:
    rows = _read_json(path)
    return [
        Ingredient(
            id=row["id"],
            name_cn=row["name_cn"],
            name_en=row.get("name_en", ""),
            inci_name=row["inci_name"],
            category=row["category"],
            functions=list(row["functions"]),
            properties=dict(row["properties"]),
            usage_range=UsageRange(**row["usage_range"]),
            regulatory_limits=list(row.get("regulatory_limits", [])),
            risk_tags=list(row.get("risk_tags", [])),
            evidence_ids=list(row.get("evidence_ids", [])),
        )
        for row in rows
    ]


def load_relations(path: Path) -> list[IngredientRelation]:
    rows = _read_json(path)
    return [IngredientRelation(**row) for row in rows]


def load_formula_requests(path: Path) -> list[FormulaRequest]:
    rows = _read_json(path)
    return [FormulaRequest(**row) for row in rows]


def load_raw_material_skus(path: Path) -> list[RawMaterialSku]:
    rows = _read_json(path)
    return [RawMaterialSku(**row) for row in rows]
