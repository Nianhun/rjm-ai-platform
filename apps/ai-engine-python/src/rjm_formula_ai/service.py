import json
from collections import Counter
from pathlib import Path
from typing import Any

from .feedback import apply_feedback_to_relations
from .feedback_store import FeedbackStore
from .formula_store import FormulaStore
from .load_data import load_ingredients, load_raw_material_skus, load_relations
from .models import FormulaRequest, Ingredient, IngredientRelation, RawMaterialSku
from .procurement import recommend_procurement_for_formula
from .recommend import recommend_formulas
from .screening_store import ScreeningStore
from .strategy import select_strategy
from .yuxi_graph_client import YuxiGraphClient


class FormulaAIService:
    def __init__(
        self,
        ingredients: list[Ingredient],
        relations: list[IngredientRelation],
        raw_material_skus: list[RawMaterialSku],
        evidence_catalog: list[dict[str, Any]] | None = None,
        formula_store: FormulaStore | None = None,
        feedback_store: FeedbackStore | None = None,
        screening_store: ScreeningStore | None = None,
        source_paths: dict[str, str] | None = None,
        yuxi_graph_client: YuxiGraphClient | None = None,
    ):
        self.ingredients = ingredients
        self.relations = relations
        self.raw_material_skus = raw_material_skus
        self.evidence_catalog = evidence_catalog or []
        self.evidence_by_id = {item.get("id"): item for item in self.evidence_catalog if item.get("id")}
        self.formula_store = formula_store
        self.feedback_store = feedback_store
        self.screening_store = screening_store
        self.source_paths = source_paths or {}
        self.yuxi_graph_client = yuxi_graph_client
        self._last_yuxi_error = ""

    @classmethod
    def from_project_root(
        cls,
        project_root: Path,
        ingredients_path: Path | None = None,
        relations_path: Path | None = None,
        raw_material_skus_path: Path | None = None,
        evidence_path: Path | None = None,
        formula_path: Path | None = None,
        feedback_path: Path | None = None,
        screening_path: Path | None = None,
        yuxi_graph_client: YuxiGraphClient | None = None,
    ) -> "FormulaAIService":
        feedback_store = FeedbackStore(feedback_path or project_root / "data" / "runtime" / "feedback_events.jsonl")
        screening_store = ScreeningStore(screening_path or project_root / "data" / "runtime" / "screening_events.jsonl")
        formula_store = FormulaStore(formula_path or project_root / "data" / "runtime" / "formula_candidates.jsonl")
        resolved_ingredients_path = ingredients_path or project_root / "data" / "samples" / "ingredients.moisturizing.json"
        resolved_relations_path = relations_path or project_root / "data" / "samples" / "ingredient_relations.moisturizing.json"
        resolved_skus_path = raw_material_skus_path or project_root / "data" / "samples" / "raw_material_skus.json"
        resolved_evidence_path = evidence_path or _default_evidence_path(project_root)
        return cls(
            ingredients=load_ingredients(resolved_ingredients_path),
            relations=load_relations(resolved_relations_path),
            raw_material_skus=load_raw_material_skus(resolved_skus_path),
            evidence_catalog=_load_evidence_catalog(resolved_evidence_path),
            formula_store=formula_store,
            feedback_store=feedback_store,
            screening_store=screening_store,
            source_paths={
                "ingredients_path": str(resolved_ingredients_path),
                "relations_path": str(resolved_relations_path),
                "raw_material_skus_path": str(resolved_skus_path),
                "evidence_path": str(resolved_evidence_path) if resolved_evidence_path else "",
                "import_batch_path": str(project_root / "data" / "yuxi_import" / "import_batch.yuxi.json")
                if (project_root / "data" / "yuxi_import" / "import_batch.yuxi.json").exists()
                else "",
                "formula_path": str(formula_store.path),
                "feedback_path": str(feedback_store.path),
                "screening_path": str(screening_store.path),
            },
            yuxi_graph_client=yuxi_graph_client,
        )

    def _relations_with_history(self) -> list[IngredientRelation]:
        if self.feedback_store is None:
            return self.relations
        return apply_feedback_to_relations(self.relations, self.feedback_store.read_all())

    def _feedback_events(self) -> list[dict[str, Any]]:
        if self.feedback_store is None:
            return []
        return self.feedback_store.read_all()

    def recommend(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        request = FormulaRequest(
            id=request_payload["id"],
            goal=request_payload["goal"],
            dosage_form=request_payload.get("dosage_form", ""),
            constraints=dict(request_payload.get("constraints", {})),
        )
        live_knowledge = self._live_formula_knowledge(request.goal)
        ingredients = live_knowledge.ingredients if live_knowledge is not None else self.ingredients
        relations = live_knowledge.relations if live_knowledge is not None else self.relations
        feedback_relations = apply_feedback_to_relations(relations, self._feedback_events())
        strategy = select_strategy(request.constraints.get("strategy"))
        if strategy.name == "baseline":
            formulas = strategy.recommend(request, ingredients, feedback_relations, [], limit=3)
        else:
            formulas = strategy.recommend(request, ingredients, relations, self._feedback_events(), limit=3)
        if self.formula_store is not None:
            self.formula_store.append_many(request.id, request.goal, formulas)
        return {
            "request_id": request.id,
            "goal": request.goal,
            "strategy": strategy.name,
            "knowledge_source": "yuxi_graph_online" if live_knowledge is not None else self._snapshot_source_name(),
            "yuxi_graph": live_knowledge.graph_stats if live_knowledge is not None else self._offline_yuxi_graph_status(),
            "formulas": formulas,
        }

    def knowledge_status(self) -> dict[str, Any]:
        evidence_prefix_counts: dict[str, int] = {}
        for evidence_id in [eid for item in self.ingredients for eid in item.evidence_ids]:
            prefix = evidence_id.split("-", 1)[0] if "-" in evidence_id else evidence_id
            evidence_prefix_counts[prefix] = evidence_prefix_counts.get(prefix, 0) + 1
        yuxi_status = self._online_yuxi_graph_status()
        return {
            "ingredient_count": len(self.ingredients),
            "relation_count": len(self.relations),
            "raw_material_sku_count": len(self.raw_material_skus),
            "evidence_count": len(self.evidence_catalog),
            "knowledge_source": "yuxi_graph_online" if yuxi_status.get("online") else self._snapshot_source_name(),
            "yuxi_graph": yuxi_status,
            "source_paths": dict(self.source_paths),
            "evidence_prefix_counts": evidence_prefix_counts,
        }

    def _live_formula_knowledge(self, goal: str):
        if self.yuxi_graph_client is None:
            return None
        try:
            self._last_yuxi_error = ""
            knowledge = self.yuxi_graph_client.recall_formula_knowledge(goal)
            if not knowledge.ingredients:
                self._last_yuxi_error = "empty_yuxi_formula_recall"
                return None
            return knowledge
        except Exception as exc:
            self._last_yuxi_error = str(exc)
            return None

    def _online_yuxi_graph_status(self) -> dict[str, Any]:
        if self.yuxi_graph_client is None:
            return self._offline_yuxi_graph_status()
        try:
            self._last_yuxi_error = ""
            return self.yuxi_graph_client.status()
        except Exception as exc:
            self._last_yuxi_error = str(exc)
            return self._offline_yuxi_graph_status()

    def _offline_yuxi_graph_status(self) -> dict[str, Any]:
        return {
            "online": False,
            "error": self._last_yuxi_error,
            "entity_count": 0,
            "relationship_count": 0,
            "total_chunks": 0,
            "indexed_chunks": 0,
            "pending_chunks": 0,
        }

    def _snapshot_source_name(self) -> str:
        return "snapshot_fallback" if self.yuxi_graph_client is not None else "local_snapshot"

    def knowledge_governance(self) -> dict[str, Any]:
        evidence_ids = set(self.evidence_by_id.keys())
        referenced_evidence_ids = {
            evidence_id
            for item in list(self.ingredients) + list(self.relations)
            for evidence_id in item.evidence_ids
        }
        missing_evidence_ids = sorted(referenced_evidence_ids - evidence_ids)
        evidence_source_type_counts = Counter(item.get("source_type", "unknown") for item in self.evidence_catalog)
        relation_type_counts = Counter(relation.relation_type for relation in self.relations)
        relation_confidence_counts = Counter(_confidence_bucket(relation.strength) for relation in self.relations)
        alias_count = sum(len(_ingredient_aliases(ingredient)) for ingredient in self.ingredients)
        warning_count = 0
        warnings: list[str] = []
        if relation_type_counts.get("synergy", 0) > 0:
            warning_count += 1
            warnings.append("Yuxi product co-occurrence edges are recommendation hints, not lab-validated synergy.")
        if missing_evidence_ids:
            warning_count += 1
            warnings.append("Some ingredient or relation evidence IDs are missing from the loaded evidence catalog.")
        if alias_count == 0:
            warning_count += 1
            warnings.append("Ingredient alias coverage is empty; standard ID matching depends on exact INCI/name fields.")

        return {
            **self.knowledge_status(),
            "evidence_source_type_counts": dict(sorted(evidence_source_type_counts.items())),
            "relation_type_counts": dict(sorted(relation_type_counts.items())),
            "relation_confidence_counts": dict(sorted(relation_confidence_counts.items())),
            "ingredient_alias_count": alias_count,
            "missing_evidence_ids": missing_evidence_ids[:20],
            "warning_count": warning_count,
            "warnings": warnings,
            "governance_notes": [
                "Keep Yuxi import files immutable per batch before production use.",
                "Treat imported relation strength as prior confidence until experiment feedback adjusts it.",
            ],
        }

    def get_evidence(self, evidence_id: str) -> dict[str, Any] | None:
        return self.evidence_by_id.get(evidence_id)

    def get_archived_formula(self, formula_id: str) -> dict[str, Any] | None:
        if self.formula_store is None:
            return None
        return self.formula_store.read_latest_by_formula(formula_id)

    def recommend_procurement(self, payload: dict[str, Any]) -> dict[str, Any]:
        return recommend_procurement_for_formula(payload["formula"], self.raw_material_skus)

    def record_feedback(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.feedback_store is None:
            raise RuntimeError("feedback store is not configured")
        count = self.feedback_store.append(payload)
        return {
            "stored": True,
            "feedback_count": count,
        }

    def record_screening(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.screening_store is None:
            raise RuntimeError("screening store is not configured")
        count = self.screening_store.append(payload)
        return {
            "stored": True,
            "screening_count": count,
        }

    def list_screening(self, formula_id: str) -> dict[str, Any]:
        if self.screening_store is None:
            raise RuntimeError("screening store is not configured")
        return {
            "formula_id": formula_id,
            "records": self.screening_store.read_by_formula(formula_id),
        }

    def feedback_recommend(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_payload = payload["request"]
        feedback_rows = list(payload.get("feedback", []))
        request = FormulaRequest(
            id=request_payload["id"],
            goal=request_payload["goal"],
            dosage_form=request_payload.get("dosage_form", ""),
            constraints=dict(request_payload.get("constraints", {})),
        )
        strategy = select_strategy(payload.get("strategy") or request.constraints.get("strategy") or "learned_weight")
        formulas = strategy.recommend(request, self.ingredients, self.relations, feedback_rows, limit=3)
        return {
            "request_id": request.id,
            "goal": request.goal,
            "strategy": strategy.name,
            "formulas": formulas,
        }


def _default_evidence_path(project_root: Path) -> Path | None:
    path = project_root / "data" / "yuxi_import" / "evidence.yuxi.json"
    return path if path.exists() else None


def _load_evidence_catalog(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _confidence_bucket(strength: float) -> str:
    if strength >= 0.75:
        return "high"
    if strength >= 0.55:
        return "medium"
    return "low"


def _ingredient_aliases(ingredient: Ingredient) -> list[str]:
    aliases = ingredient.properties.get("aliases", [])
    return aliases if isinstance(aliases, list) else []
