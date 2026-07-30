from __future__ import annotations

import json
from http.client import HTTPConnection
import csv
from io import StringIO
import os
import re
import subprocess
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

    def list_entities(self, kb_id: str, label: str = "Ingredient", limit: int = 100000) -> list[dict[str, Any]]:
        try:
            payload = self._get_json(
                "/api/graph/entities?"
                + urlencode(
                    {
                        "kb_id": kb_id,
                        "label": label,
                        "limit": limit,
                        "offset": 0,
                    }
                )
            )
            data = dict(payload.get("data") or {})
            return list(data.get("entities") or [])
        except RuntimeError as exc:
            if "yuxi_http_404" not in str(exc):
                raise
            return _list_entities_from_local_postgres(kb_id, label=label, limit=limit)

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
        self._entity_name_map: dict[str, str] | None = None

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

    def recall_chat_knowledge(self, question: str, max_nodes: int = 80) -> FormulaKnowledge:
        status = self.status()
        query = _chat_entity_query(question, self.entity_name_map())
        subgraph = self.gateway.get_subgraph(
            status["kb_id"],
            keyword=query,
            max_depth=1,
            max_nodes=max_nodes,
            exclude_chunk=True,
        )
        nodes = _display_nodes_from_subgraph(subgraph.get("nodes") or [], max_nodes)
        if not nodes:
            return self.recall_formula_knowledge(question, max_ingredients=max_nodes)
        public_id_by_graph_id = {node["graph_id"]: node["id"] for node in nodes}
        ingredients = _knowledge_items_from_display_nodes(nodes, question)
        relations = _knowledge_relations_from_display_edges(
            _display_edges_from_subgraph(subgraph.get("edges") or [], public_id_by_graph_id, max_nodes),
        )
        evidence = [_evidence_from_ingredient(item) for item in ingredients]
        return FormulaKnowledge(
            ingredients=ingredients,
            relations=relations,
            evidence_catalog=evidence,
            graph_stats=status,
        )

    def element_graph(self, element_id: str, max_nodes: int = 56) -> dict[str, Any]:
        status = self.status()
        query = str(element_id or "").strip()
        subgraph = self.gateway.get_subgraph(
            status["kb_id"],
            keyword=query,
            max_depth=1,
            max_nodes=max_nodes,
            exclude_chunk=True,
        )
        nodes = _display_nodes_from_subgraph(subgraph.get("nodes") or [], max_nodes)
        if not nodes:
            return _empty_element_graph(query)
        center = _select_center_node(query, nodes)
        public_id_by_graph_id = {node["graph_id"]: node["id"] for node in nodes}
        edges = _display_edges_from_subgraph(subgraph.get("edges") or [], public_id_by_graph_id, max_nodes)
        return {
            "query": query,
            "center": _public_node(center),
            "nodes": [_public_node(node) for node in nodes],
            "edges": edges,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "truncated": len(subgraph.get("nodes") or []) > len(nodes) or len(subgraph.get("edges") or []) > len(edges),
            },
        }

    def entity_name_map(self) -> dict[str, str]:
        if self._entity_name_map is not None:
            return dict(self._entity_name_map)
        getter = getattr(self.gateway, "list_entities", None)
        if not callable(getter):
            self._entity_name_map = {}
            return {}
        rows = getter(self._resolve_kb_id(), label="", limit=100000)
        mapping: dict[str, str] = {}
        for row in rows:
            entity_id = str(row.get("entity_id") or "").strip()
            name = str(row.get("name") or row.get("normalized_name") or "").strip()
            if not entity_id or not name or _is_yuxi_public_id(name):
                continue
            mapping["YUXI-" + _slug(entity_id)] = name
        self._entity_name_map = mapping
        return dict(mapping)

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


def _knowledge_items_from_display_nodes(nodes: list[dict[str, Any]], goal: str) -> list[Ingredient]:
    ingredients: list[Ingredient] = []
    for node in nodes:
        label = str(node.get("label") or "").strip()
        if not label:
            continue
        properties = dict(node.get("properties") or {})
        properties["node_type"] = node.get("type") or properties.get("label") or "Entity"
        ingredients.append(
            Ingredient(
                id=str(node.get("id") or "YUXI-" + _slug(label)),
                name_cn=label,
                name_en=label,
                inci_name=label.upper(),
                category=str(node.get("type") or properties.get("label") or "Entity"),
                functions=[goal],
                properties=properties,
                usage_range=UsageRange(min_percent=0.0, max_percent=0.0, typical_percent=0.0),
                regulatory_limits=[],
                risk_tags=[],
                evidence_ids=["YUXI-GRAPH-" + _slug(node.get("id") or label)],
            )
        )
    return ingredients


def _knowledge_relations_from_display_edges(edges: list[dict[str, Any]]) -> list[IngredientRelation]:
    relations: list[IngredientRelation] = []
    for edge in edges:
        relation_type = str(edge.get("label") or edge.get("type") or "relation")
        relations.append(
            IngredientRelation(
                id="YUXI-REL-" + _slug(edge.get("id") or f"{edge.get('source')}-{edge.get('target')}-{relation_type}"),
                source_ingredient_id=str(edge.get("source") or ""),
                target_ingredient_id=str(edge.get("target") or ""),
                relation_type=relation_type,
                description=str(edge.get("description") or relation_type),
                strength=0.65,
                feedback_weight=0.0,
                evidence_ids=["YUXI-GRAPH-REL-" + _slug(edge.get("id") or f"{edge.get('source')}-{edge.get('target')}")],
            )
        )
    return relations


def _display_nodes_from_subgraph(nodes: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    display_nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in nodes:
        node_type = _node_type(node).lower()
        node_kind = _node_kind(node).lower()
        if node_type == "chunk" or node_kind == "chunk":
            continue
        label = _node_name(node)
        graph_id = str(node.get("id") or _node_entity_id(node) or label).strip()
        if not label or not graph_id or graph_id in seen:
            continue
        seen.add(graph_id)
        entity_id = _node_entity_id(node)
        display_nodes.append(
            {
                "graph_id": graph_id,
                "id": "YUXI-" + _slug(entity_id or graph_id or label),
                "label": label,
                "type": _node_kind(node) or _node_type(node) or "Entity",
                "description": str((node.get("properties") or {}).get("description") or ""),
                "properties": dict(node.get("properties") or {}),
            }
        )
        if len(display_nodes) >= limit:
            break
    return display_nodes


def _display_edges_from_subgraph(edges: list[dict[str, Any]], public_id_by_graph_id: dict[str, str], limit: int) -> list[dict[str, Any]]:
    display_edges: list[dict[str, Any]] = []
    for edge in edges:
        source_graph_id = str(edge.get("source_id") or "")
        target_graph_id = str(edge.get("target_id") or "")
        source_public_id = public_id_by_graph_id.get(source_graph_id)
        target_public_id = public_id_by_graph_id.get(target_graph_id)
        if not source_public_id or not target_public_id:
            continue
        properties = dict(edge.get("properties") or {})
        relation_type = str(properties.get("relation_type") or edge.get("type") or "relation")
        display_edges.append(
            {
                "id": str(edge.get("id") or f"{source_graph_id}-{target_graph_id}-{relation_type}"),
                "source": source_public_id,
                "target": target_public_id,
                "label": relation_type,
                "type": relation_type,
                "description": str(properties.get("content") or properties.get("description") or ""),
            }
        )
        if len(display_edges) >= limit:
            break
    return display_edges


def _select_center_node(query: str, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_query = query.upper()
    for node in nodes:
        candidates = {node["id"].upper(), node["graph_id"].upper(), str(node["properties"].get("entity_id", "")).upper()}
        if normalized_query in candidates:
            return node
    return nodes[0]


def _public_node(node: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in node.items() if key != "graph_id"}


def _empty_element_graph(query: str) -> dict[str, Any]:
    return {
        "query": query,
        "nodes": [],
        "edges": [],
        "stats": {"node_count": 0, "edge_count": 0, "truncated": False},
    }


def _chat_entity_query(question: str, entity_names: dict[str, str]) -> str:
    text = str(question or "").strip()
    lowered = text.lower()
    matches = [
        name
        for name in entity_names.values()
        if name and len(name) >= 3 and name.lower() in lowered
    ]
    if matches:
        return max(matches, key=len)
    return text


def _evidence_from_ingredient(ingredient: Ingredient) -> dict[str, Any]:
    title = ingredient.name_cn or ingredient.name_en or ingredient.inci_name or ingredient.id
    return {
        "id": ingredient.evidence_ids[0],
        "source_type": "yuxi_graph_entity",
        "title": title,
        "summary": str(ingredient.properties.get("description") or title)[:500],
        "source_url": "",
        "metadata": {
            "ingredient_id": ingredient.id,
            "ingredient_name": title,
            "name_cn": ingredient.name_cn,
            "name_en": ingredient.name_en,
            "inci_name": ingredient.inci_name,
            "category": ingredient.category,
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


def _is_yuxi_public_id(value: str) -> bool:
    return bool(re.fullmatch(r"YUXI-[A-Z0-9-]+", value.strip().upper()))


def _list_entities_from_local_postgres(kb_id: str, *, label: str, limit: int) -> list[dict[str, Any]]:
    container = os.environ.get("RJM_YUXI_POSTGRES_CONTAINER", "postgres")
    user = os.environ.get("RJM_YUXI_POSTGRES_USER", "postgres")
    database = os.environ.get("RJM_YUXI_POSTGRES_DATABASE", "yuxi")
    safe_limit = max(1, min(int(limit or 100000), 100000))
    where = f"kb_id = {_sql_literal(kb_id)}"
    if label:
        where += f" and label = {_sql_literal(label)}"
    sql = (
        "COPY ("
        "select entity_id,name,normalized_name,label "
        "from knowledge_graph_entities "
        f"where {where} "
        "order by name "
        f"limit {safe_limit}"
        ") TO STDOUT WITH CSV HEADER"
    )
    completed = subprocess.run(
        ["docker", "exec", container, "psql", "-U", user, "-d", database, "-c", sql],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=float(os.environ.get("RJM_YUXI_POSTGRES_TIMEOUT_SECONDS", "30")),
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"yuxi_entity_names_unavailable:{completed.stderr.strip()[:300]}")
    return [dict(row) for row in csv.DictReader(StringIO(completed.stdout))]


def _sql_literal(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"
