from __future__ import annotations

import json
import subprocess
from http.client import HTTPConnection, HTTPSConnection
from typing import Any
from urllib.parse import urlparse

from .models import FormulaRequest
from .yuxi_graph_client import FormulaKnowledge


LANGUAGE_POLICY = (
    "Language policy: all explanatory prose must be Simplified Chinese, including "
    "recommendation_reason, risk_notes, answer, follow_up_questions, and any narrative comments. "
    "Keep ingredient names, INCI names, ingredient IDs, evidence IDs, and formula IDs exactly as supplied "
    "or in English/original form; do not translate ingredient names."
)

LANGUAGE_RETRY_PROMPT = (
    "Your previous JSON used non-Chinese explanatory prose. Regenerate the same JSON structure. "
    "All explanatory prose must be Simplified Chinese. Keep ingredient names, INCI names, ingredient IDs, "
    "evidence IDs, and formula IDs exactly as supplied or in English/original form."
)


class OpenAICompatibleFormulaAnalyzer:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 120.0,
        chat_completions_path: str = "/chat/completions",
        http_client: str = "python",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.chat_completions_path = chat_completions_path if chat_completions_path.startswith("/") else f"/{chat_completions_path}"
        self.http_client = http_client

    def recommend(
        self,
        request: FormulaRequest,
        knowledge: FormulaKnowledge,
        feedback_events: list[dict[str, Any]],
        strategy_name: str,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a cosmetic formulation R&D analyst. Use only the supplied Yuxi graph "
                        "ingredients, relations, evidence, request, and feedback. Return strict JSON only. "
                        "Do not invent ingredients or cite evidence IDs that were not supplied. "
                        + LANGUAGE_POLICY
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": "Generate evidence-backed formula candidates from Yuxi graph recall.",
                            "output_contract": {
                                "formulas": [
                                    {
                                        "id": "string",
                                        "ingredients": [
                                            {
                                                "ingredient_id": "must be one supplied ingredient id",
                                                "role": "Simplified Chinese role label; keep supplied ingredient/category terms in English if used",
                                                "suggested_percent_min": "number",
                                                "suggested_percent_max": "number",
                                            }
                                        ],
                                        "recommendation_reason": "Simplified Chinese prose; ingredient names remain English/INCI",
                                        "risk_notes": ["Simplified Chinese prose; ingredient names remain English/INCI"],
                                        "evidence_ids": ["must be supplied evidence id"],
                                        "score": {
                                            "efficacy": "0..1",
                                            "stability": "0..1",
                                            "skin_feel": "0..1",
                                            "cost": "0..1",
                                            "supply": "0..1",
                                            "overall": "0..1",
                                        },
                                    }
                                ]
                            },
                            "request": {
                                "id": request.id,
                                "goal": request.goal,
                                "dosage_form": request.dosage_form,
                                "constraints": request.constraints,
                                "strategy": strategy_name,
                                "limit": limit,
                            },
                            "yuxi_graph": {
                                "stats": knowledge.graph_stats,
                                "ingredients": [_ingredient_payload(item) for item in knowledge.ingredients],
                                "relations": [_relation_payload(item) for item in knowledge.relations],
                                "evidence": knowledge.evidence_catalog,
                            },
                            "feedback_events": feedback_events[-20:],
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
        }
        response = self._post_json(self.chat_completions_path, payload)
        content = response["choices"][0]["message"]["content"]
        try:
            return normalize_ai_formulas(json.loads(content), request, knowledge, strategy_name, limit)
        except RuntimeError as exc:
            if str(exc) != "ai_provider_text_must_be_simplified_chinese":
                raise
        payload["messages"].append({"role": "user", "content": LANGUAGE_RETRY_PROMPT})
        response = self._post_json(self.chat_completions_path, payload)
        content = response["choices"][0]["message"]["content"]
        return normalize_ai_formulas(json.loads(content), request, knowledge, strategy_name, limit)

    def chat(
        self,
        question: str,
        knowledge: FormulaKnowledge,
        history: list[dict[str, str]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        evidence_ids = [item.get("id") for item in knowledge.evidence_catalog if item.get("id")]
        ingredient_ids = [item.id for item in knowledge.ingredients]
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a cosmetic formulation R&D assistant. Answer formulators using only the supplied "
                        "Yuxi knowledge graph recall and conversation context. Return strict JSON only. If the graph "
                        "does not support a conclusion, say what is missing instead of guessing. "
                        "When the user asks for a formula, return concrete formula_ingredients with display names, "
                        "suggested concentrations, efficacy classes, and core effects. Do not use ingredient IDs as "
                        "human-facing ingredient or formula names when display names are supplied. "
                        + LANGUAGE_POLICY
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": "Answer the formulator's question using Yuxi graph knowledge.",
                            "output_contract": {
                                "answer": "Simplified Chinese prose; ingredient names remain English/INCI",
                                "formula_ingredients": [
                                    {
                                        "ingredient_id": "must be supplied ingredient id when available",
                                        "name": "ingredient display name",
                                        "concentration": "suggested percentage such as 5% or 至100%",
                                        "function_group": "Simplified Chinese efficacy class such as 抑黑, 还原, 保湿",
                                        "core_effect": "Simplified Chinese effect summary",
                                    }
                                ],
                                "function_groups": [
                                    {
                                        "name": "Simplified Chinese efficacy class",
                                        "ingredient_ids": ["supplied ingredient ids"],
                                    }
                                ],
                                "relation_edges": [
                                    {
                                        "source": "ingredient id or function group",
                                        "target": "ingredient id or function group",
                                        "label": "Simplified Chinese relation label",
                                    }
                                ],
                                "core_path": ["Simplified Chinese numbered synthesis path"],
                                "follow_up_questions": ["Simplified Chinese questions; ingredient names remain English/INCI"],
                                "ingredient_ids": ["must be supplied ingredient id"],
                                "evidence_ids": ["must be supplied evidence id"],
                            },
                            "question": question,
                            "context": context or {},
                            "history": history or [],
                            "yuxi_graph": {
                                "stats": knowledge.graph_stats,
                                "ingredients": [_ingredient_payload(item) for item in knowledge.ingredients],
                                "relations": [_relation_payload(item) for item in knowledge.relations],
                                "evidence": knowledge.evidence_catalog,
                            },
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "response_format": {"type": "json_object"},
        }
        response = self._post_json(self.chat_completions_path, payload)
        content = response["choices"][0]["message"]["content"]
        result = json.loads(content)
        try:
            return normalize_ai_chat(result, ingredient_ids, evidence_ids)
        except RuntimeError as exc:
            if str(exc) != "ai_provider_text_must_be_simplified_chinese":
                raise
        payload["messages"].append({"role": "user", "content": LANGUAGE_RETRY_PROMPT})
        response = self._post_json(self.chat_completions_path, payload)
        content = response["choices"][0]["message"]["content"]
        result = json.loads(content)
        return normalize_ai_chat(result, ingredient_ids, evidence_ids)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.http_client == "curl":
            return self._post_json_with_curl(path, payload)
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"}:
            raise RuntimeError("ai_provider_base_url_must_be_http_or_https")
        connection_cls = HTTPSConnection if parsed.scheme == "https" else HTTPConnection
        connection = connection_cls(parsed.hostname, parsed.port, timeout=self.timeout_seconds)
        request_path = (parsed.path.rstrip("/") if parsed.path else "") + path
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            connection.request("POST", request_path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read().decode("utf-8")
            if response.status >= 400:
                raise RuntimeError(f"ai_provider_http_{response.status}: {raw[:300]}")
            return json.loads(raw)
        finally:
            connection.close()

    def _post_json_with_curl(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self.base_url + path
        body = json.dumps(payload, ensure_ascii=False)
        completed = subprocess.run(
            [
                "curl.exe",
                "--silent",
                "--show-error",
                "--fail-with-body",
                "--max-time",
                str(int(self.timeout_seconds)),
                "-X",
                "POST",
                url,
                "-H",
                f"Authorization: Bearer {self.api_key}",
                "-H",
                "Content-Type: application/json",
                "-H",
                "Accept: application/json",
                "--data-binary",
                "@-",
            ],
            input=body,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode != 0:
            detail = (completed.stdout or completed.stderr).strip()
            raise RuntimeError(f"ai_provider_curl_failed:{detail[:300]}")
        return json.loads(completed.stdout)


def normalize_ai_chat(result: dict[str, Any], ingredient_ids: list[str], evidence_ids: list[str]) -> dict[str, Any]:
    answer = _required_chinese_text(result, "answer")
    follow_up_questions = _chinese_text_list(result.get("follow_up_questions", []))
    return {
        "answer": answer,
        "follow_up_questions": follow_up_questions,
        "ingredient_ids": _known_ids(result.get("ingredient_ids", []), set(ingredient_ids), "ingredient"),
        "evidence_ids": _known_ids(result.get("evidence_ids", []), set(evidence_ids), "evidence"),
        "formula_ingredients": _dict_list(result.get("formula_ingredients", [])),
        "function_groups": _dict_list(result.get("function_groups", [])),
        "relation_edges": _dict_list(result.get("relation_edges", [])),
        "core_path": _text_list(result.get("core_path", [])),
    }


def normalize_ai_formulas(
    payload: dict[str, Any],
    request: FormulaRequest,
    knowledge: FormulaKnowledge,
    strategy_name: str,
    limit: int,
) -> list[dict[str, Any]]:
    formulas = payload.get("formulas")
    if not isinstance(formulas, list) or not formulas:
        raise RuntimeError("ai_provider_returned_no_formulas")
    ingredient_by_id = {item.id: item for item in knowledge.ingredients}
    allowed_ingredient_ids = set(ingredient_by_id)
    allowed_evidence_ids = {evidence.get("id") for evidence in knowledge.evidence_catalog if evidence.get("id")}
    normalized = []
    for index, formula in enumerate(formulas[:limit], start=1):
        if not isinstance(formula, dict):
            raise RuntimeError("ai_provider_formula_must_be_object")
        ingredients = _normalize_ingredients(formula.get("ingredients"), ingredient_by_id)
        evidence_ids = _normalize_evidence_ids(formula.get("evidence_ids"), allowed_evidence_ids)
        score = _normalize_score(formula.get("score"))
        normalized.append(
            {
                "id": str(formula.get("id") or f"AI-FORM-{index:03d}"),
                "request_id": request.id,
                "goal": request.goal,
                "strategy": strategy_name,
                "ingredients": ingredients,
                "recommendation_reason": _required_chinese_text(formula, "recommendation_reason"),
                "risk_notes": _chinese_text_list(formula.get("risk_notes", [])),
                "evidence_ids": evidence_ids,
                "score": score,
                "status": "ai_recommended",
            }
        )
    return normalized


def _normalize_ingredients(value: Any, ingredient_by_id: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RuntimeError("ai_provider_formula_requires_ingredients")
    normalized = []
    for item in value:
        ingredient_id = str(item.get("ingredient_id") or "")
        ingredient = ingredient_by_id.get(ingredient_id)
        if ingredient is None:
            raise RuntimeError(f"ai_provider_used_unknown_ingredient:{ingredient_id}")
        role = str(item.get("role") or "").strip()
        if not role or not _contains_cjk(role):
            raise RuntimeError("ai_provider_text_must_be_simplified_chinese")
        normalized.append(
            {
                "ingredient_id": ingredient_id,
                "name": item.get("name") or ingredient.name_cn or ingredient.name_en or ingredient.inci_name or ingredient.id,
                "name_cn": ingredient.name_cn,
                "name_en": ingredient.name_en,
                "inci_name": ingredient.inci_name,
                "category": ingredient.category,
                "evidence_ids": list(ingredient.evidence_ids),
                "role": role,
                "suggested_percent_min": float(item.get("suggested_percent_min")),
                "suggested_percent_max": float(item.get("suggested_percent_max")),
            }
        )
    return normalized


def _normalize_evidence_ids(value: Any, allowed_evidence_ids: set[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RuntimeError("ai_provider_formula_requires_evidence_ids")
    evidence_ids = [str(item) for item in value]
    unknown = [item for item in evidence_ids if item not in allowed_evidence_ids]
    if unknown:
        raise RuntimeError(f"ai_provider_used_unknown_evidence:{unknown[0]}")
    return evidence_ids


def _known_ids(value: Any, allowed_ids: set[str], label: str) -> list[str]:
    if not isinstance(value, list):
        return []
    known = [str(item) for item in value if str(item) in allowed_ids]
    if not known and allowed_ids:
        return []
    return known


def _normalize_score(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        raise RuntimeError("ai_provider_formula_requires_score")
    return {
        key: _score(value, key)
        for key in ["efficacy", "stability", "skin_feel", "cost", "supply", "overall"]
    }


def _score(value: dict[str, Any], key: str) -> float:
    score = float(value[key])
    if score < 0 or score > 1:
        raise RuntimeError(f"ai_provider_score_out_of_range:{key}")
    return score


def _required_text(payload: dict[str, Any], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise RuntimeError(f"ai_provider_formula_requires_{key}")
    return value


def _required_chinese_text(payload: dict[str, Any], key: str) -> str:
    value = _required_text(payload, key)
    if not _contains_cjk(value):
        raise RuntimeError("ai_provider_text_must_be_simplified_chinese")
    return value


def _chinese_text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items = [str(item).strip() for item in value if str(item).strip()]
    if any(not _contains_cjk(item) for item in items):
        raise RuntimeError("ai_provider_text_must_be_simplified_chinese")
    return items


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _contains_cjk(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)


def _ingredient_payload(item: Any) -> dict[str, Any]:
    return {
        "id": item.id,
        "name_cn": item.name_cn,
        "name_en": item.name_en,
        "inci_name": item.inci_name,
        "category": item.category,
        "functions": item.functions,
        "properties": item.properties,
        "usage_range": {
            "min_percent": item.usage_range.min_percent,
            "max_percent": item.usage_range.max_percent,
            "typical_percent": item.usage_range.typical_percent,
        },
        "regulatory_limits": item.regulatory_limits,
        "risk_tags": item.risk_tags,
        "evidence_ids": item.evidence_ids,
    }


def _relation_payload(item: Any) -> dict[str, Any]:
    return {
        "id": item.id,
        "source_ingredient_id": item.source_ingredient_id,
        "target_ingredient_id": item.target_ingredient_id,
        "relation_type": item.relation_type,
        "description": item.description,
        "strength": item.strength,
        "feedback_weight": item.feedback_weight,
        "evidence_ids": item.evidence_ids,
    }
