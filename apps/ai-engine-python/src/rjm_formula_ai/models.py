from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UsageRange:
    min_percent: float
    max_percent: float
    typical_percent: float


@dataclass(frozen=True)
class Ingredient:
    id: str
    name_cn: str
    name_en: str
    inci_name: str
    category: str
    functions: list[str]
    properties: dict[str, Any]
    usage_range: UsageRange
    regulatory_limits: list[str]
    risk_tags: list[str]
    evidence_ids: list[str]


@dataclass(frozen=True)
class IngredientRelation:
    id: str
    source_ingredient_id: str
    target_ingredient_id: str
    relation_type: str
    description: str
    strength: float
    feedback_weight: float
    evidence_ids: list[str]


@dataclass(frozen=True)
class FormulaRequest:
    id: str
    goal: str
    dosage_form: str
    constraints: dict[str, Any]


@dataclass(frozen=True)
class RawMaterialSku:
    id: str
    ingredient_id: str
    supplier_id: str
    specification: str
    price: dict[str, Any]
    moq_kg: float
    lead_time_days: int
    qualification_files: list[str]
    sample_status: str
    quality_rating: float
