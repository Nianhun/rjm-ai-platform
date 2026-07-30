from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any

from .feedback import apply_feedback_to_relations
from .models import FormulaRequest, Ingredient, IngredientRelation
from .recommend import recommend_formulas


class RecommendationStrategy(ABC):
    name: str

    @abstractmethod
    def recommend(
        self,
        request: FormulaRequest,
        ingredients: list[Ingredient],
        relations: list[IngredientRelation],
        feedback_events: list[dict[str, Any]],
        limit: int = 3,
    ) -> list[dict]:
        raise NotImplementedError


class BaselineRecommendationStrategy(RecommendationStrategy):
    name = "knowledge_graph_ai"

    def recommend(
        self,
        request: FormulaRequest,
        ingredients: list[Ingredient],
        relations: list[IngredientRelation],
        feedback_events: list[dict[str, Any]],
        limit: int = 3,
    ) -> list[dict]:
        formulas = recommend_formulas(request, ingredients, relations, limit=limit)
        return [_with_strategy(formula, self.name) for formula in formulas]


class LearnedWeightRecommendationStrategy(RecommendationStrategy):
    name = "learned_weight"

    def recommend(
        self,
        request: FormulaRequest,
        ingredients: list[Ingredient],
        relations: list[IngredientRelation],
        feedback_events: list[dict[str, Any]],
        limit: int = 3,
    ) -> list[dict]:
        updated_relations = apply_feedback_to_relations(relations, feedback_events)
        formulas = recommend_formulas(request, ingredients, updated_relations, limit=limit)
        return [_with_strategy(formula, self.name) for formula in formulas]


class ExplorationRecommendationStrategy(RecommendationStrategy):
    name = "exploration"

    def recommend(
        self,
        request: FormulaRequest,
        ingredients: list[Ingredient],
        relations: list[IngredientRelation],
        feedback_events: list[dict[str, Any]],
        limit: int = 3,
    ) -> list[dict]:
        formulas = recommend_formulas(request, ingredients, relations, limit=limit)
        explored = []
        for formula in formulas:
            item = _with_strategy(formula, self.name)
            evidence_count = len(item.get("evidence_ids", []))
            risk_count = len(item.get("risk_notes", []))
            exploration_bonus = 0.015 if evidence_count <= 3 and risk_count == 0 else 0.0
            item["score"]["exploration_bonus"] = round(exploration_bonus, 3)
            item["score"]["overall"] = round(min(1.0, item["score"]["overall"] + exploration_bonus), 3)
            explored.append(item)
        return sorted(explored, key=lambda item: item["score"]["overall"], reverse=True)


_STRATEGIES: dict[str, RecommendationStrategy] = {
    strategy.name: strategy
    for strategy in [
        BaselineRecommendationStrategy(),
        LearnedWeightRecommendationStrategy(),
        ExplorationRecommendationStrategy(),
    ]
}
_STRATEGIES["baseline"] = _STRATEGIES["knowledge_graph_ai"]


def available_strategy_names() -> list[str]:
    return [name for name in _STRATEGIES.keys() if name != "baseline"]


def select_strategy(name: str | None) -> RecommendationStrategy:
    if not name:
        return _STRATEGIES["knowledge_graph_ai"]
    return _STRATEGIES.get(name, _STRATEGIES["knowledge_graph_ai"])


def _with_strategy(formula: dict, strategy_name: str) -> dict:
    item = deepcopy(formula)
    item["strategy"] = strategy_name
    return item
