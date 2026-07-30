from __future__ import annotations

import json
from http.client import HTTPConnection
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlparse

from .models import Ingredient, IngredientRelation, UsageRange


@dataclass(frozen=True)
class FormulaKnowledge:
    ingredients: list[Ingredient]
    relations: list[IngredientRelation]
    evidence_catalog: list[dict[str, Any]]
    graph_stats: dict[str, Any]


class HttpYuxiGateway:
    def __init__(self, base_url: str, token: str | None = None, timeout_seconds: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds

    def list_graphs(self) -> list[dict[str, Any]]:
        payload = self._get_json("/api/graph/list")
        return list(payload.get("data") or [])

    def get_graph_stats(self, kb_id: str) -> dict[str, Any]:
        payload = self._get_json("/api/graph/stats?" + urlencode({"kb_id": kb_id}))
        return dict(payload.get("data") or {})

    def get_graph_build_status(self, kb_id: str) -> dict[str, Any]:
        payload = self._get_json(f"/api/knowledge/databases/{kb_id}/graph-build/status")
        return dict(payload.get("data") or payload)

    def get_subgraph(
        self,
        kb_id: str,
        keyword: str,
        max_depth: int,
        max_nodes: int,
        exclude_chunk: bool,
    ) -> dict[str, Any]:
        payload = self._get_json(
            "/api/graph/subgraph?"
            + urlencode(
                {
                    "kb_id": kb_id,
                    "node_label": keyword,
                    "max_depth": max_depth,
                    "max_nodes": max_nodes,
                    "exclude_chunk": str(exclude_chunk).lower(),
                }
            )
        )
        return dict(payload.get("data") or {})

    def _get_json(self, path: str) -> dict[str, Any]:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "http":
            raise RuntimeError("yuxi_http_only_gateway_requires_http_base_url")
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        connection = HTTPConnection(parsed.hostname, parsed.port or 80, timeout=self.timeout_seconds)
        request_path = (parsed.path.rstrip("/") if parsed.path else "") + path
        try:
            connection.request("GET", request_path, headers=headers)
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            if response.status >= 400:
                raise RuntimeError(f"yuxi_http_{response.status}: {body[:300]}")
            return json.loads(body)
        finally:
            connection.close()


class YuxiGraphClient:
    def __init__(self, gateway: Any, kb_id: str | None = None):
        self.gateway = gateway
        self._kb_id = kb_id

    def status(self) -> dict[str, Any]:
        kb_id = self._resolve_kb_id()
        stats = self.gateway.get_graph_stats(kb_id)
        build_status = _optional_graph_build_status(self.gateway, kb_id)
        merged_stats = {**stats, **build_status}
        return {
            "online": True,
            "kb_id": kb_id,
            "total_chunks": _int_first(merged_stats, "total_chunks", "indexed_chunks", "chunk_count"),
            "indexed_chunks": _int_first(merged_stats, "indexed_chunks", "total_chunks"),
            "pending_chunks": _int_first(merged_stats, "pending_chunks"),
            "entity_count": _int_first(merged_stats, "entity_count", "total_nodes"),
            "relationship_count": _int_first(merged_stats, "relationship_count", "total_edges"),
            "raw": merged_stats,
        }

    def recall_formula_knowledge(self, goal: str, max_ingredients: int = 80) -> FormulaKnowledge:
        status = self.status()
        subgraph = self.gateway.get_subgraph(
            status["kb_id"],
            keyword=goal,
            max_depth=2,
            max_nodes=max(max_ingredients * 4, 50),
            exclude_chunk=False,
        )
        ingredients = _ingredients_from_nodes(subgraph.get("nodes") or [], goal, max_ingredients)
        if not ingredients:
            subgraph = self.gateway.get_subgraph(
                status["kb_id"],
                keyword="*",
                max_depth=1,
                max_nodes=max(max_ingredients * 4, 50),
                exclude_chunk=False,
            )
        ingredients = _ingredients_from_nodes(subgraph.get("nodes") or [], goal, max_ingredients)
        ingredient_id_by_graph_node_id: dict[str, str] = {}
        for item in ingredients:
            ingredient_id_by_graph_node_id[str(item.properties.get("yuxi_entity_id") or "")] = item.id
            ingredient_id_by_graph_node_id[str(item.properties.get("yuxi_node_id") or "")] = item.id
        relations = _relations_from_edges(subgraph.get("edges") or [], ingredient_id_by_graph_node_id)
        evidence = [_evidence_from_ingredient(item) for item in ingredients]
        return FormulaKnowledge(
            ingredients=ingredients,
            relations=relations,
            evidence_catalog=evidence,
            graph_stats=status,
        )

    def _resolve_kb_id(self) -> str:
        if self._kb_id:
            return self._kb_id
        graphs = self.gateway.list_graphs()
        if not graphs:
            raise RuntimeError("no_yuxi_graph_available")
        self._kb_id = str(graphs[0]["id"])
        return self._kb_id


def _ingredients_from_nodes(nodes: list[dict[str, Any]], goal: str, limit: int) -> list[Ingredient]:
    ingredients: list[Ingredient] = []
    seen: set[str] = set()
    for node in nodes:
        node_type = _node_type(node).lower()
        node_kind = _node_kind(node).lower()
        if node_type == "chunk" or node_kind == "chunk" or (node_kind and node_kind != "ingredient"):
            continue
        name = _node_name(node)
        if not name:
            continue
        entity_id = _node_entity_id(node)
        ingredient_id = "YUXI-" + _slug(entity_id or name)
        if ingredient_id in seen:
            continue
        seen.add(ingredient_id)
        properties = dict(node.get("properties") or {})
        properties["yuxi_entity_id"] = entity_id or node.get("id") or name
        properties["yuxi_node_id"] = str(node.get("id") or "")
        ingredients.append(
            Ingredient(
                id=ingredient_id,
                name_cn=name,
                name_en=name,
                inci_name=name.upper(),
                category=_category_from_text(name + " " + str(properties)),
                functions=[goal],
                properties=properties,
                usage_range=UsageRange(min_percent=0.1, max_percent=5.0, typical_percent=1.0),
                regulatory_limits=[],
                risk_tags=[],
                evidence_ids=["YUXI-GRAPH-" + _slug(entity_id or name)],
            )
        )
        if len(ingredients) >= limit:
            break
    return ingredients


def _relations_from_edges(edges: list[dict[str, Any]], ingredient_id_by_entity_id: dict[str, str]) -> list[IngredientRelation]:
    relations: list[IngredientRelation] = []
    for edge in edges:
        source = ingredient_id_by_entity_id.get(str(edge.get("source_id") or ""))
        target = ingredient_id_by_entity_id.get(str(edge.get("target_id") or ""))
        if not source or not target:
            continue
        properties = dict(edge.get("properties") or {})
        relation_type = str(properties.get("relation_type") or edge.get("type") or "synergy").lower()
        relations.append(
            IngredientRelation(
                id="YUXI-REL-" + _slug(edge.get("id") or f"{source}-{target}-{relation_type}"),
                source_ingredient_id=source,
                target_ingredient_id=target,
                relation_type="synergy" if relation_type in {"relation", "cooccur", "co_occurrence"} else relation_type,
                description=str(properties.get("content") or properties.get("description") or "Yuxi graph relationship"),
                strength=0.65,
                feedback_weight=0.0,
                evidence_ids=["YUXI-GRAPH-REL-" + _slug(edge.get("id") or f"{source}-{target}")],
            )
        )
    return relations


def _evidence_from_ingredient(ingredient: Ingredient) -> dict[str, Any]:
    return {
        "id": ingredient.evidence_ids[0],
        "source_type": "yuxi_graph_entity",
        "title": ingredient.name_en,
        "summary": str(ingredient.properties.get("description") or ingredient.name_en)[:500],
        "source_url": "",
        "metadata": {
            "ingredient_id": ingredient.id,
            "yuxi_entity_id": ingredient.properties.get("yuxi_entity_id", ""),
        },
    }


def _node_type(node: dict[str, Any]) -> str:
    return str(node.get("type") or node.get("label") or (node.get("properties") or {}).get("label") or "")


def _node_kind(node: dict[str, Any]) -> str:
    properties = dict(node.get("properties") or {})
    normalized = dict(node.get("normalized") or {})
    return str(normalized.get("type") or properties.get("label") or node.get("type") or "")


def _node_name(node: dict[str, Any]) -> str:
    properties = dict(node.get("properties") or {})
    return str(node.get("name") or properties.get("name") or properties.get("entity_name") or "").strip()


def _node_entity_id(node: dict[str, Any]) -> str:
    properties = dict(node.get("properties") or {})
    return str(properties.get("entity_id") or node.get("id") or "").strip()


def _category_from_text(text: str) -> str:
    lowered = text.lower()
    if "humectant" in lowered:
        return "humectant"
    if "emollient" in lowered:
        return "emollient"
    if "barrier" in lowered:
        return "barrier_active"
    return "active"


def _int_first(payload: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return int(value)
    return 0


def _optional_graph_build_status(gateway: Any, kb_id: str) -> dict[str, Any]:
    getter = getattr(gateway, "get_graph_build_status", None)
    if not callable(getter):
        return {}
    try:
        return dict(getter(kb_id) or {})
    except Exception:
        return {}


def _slug(value: Any) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(value).upper()).strip("-")
    return slug or "UNKNOWN"
