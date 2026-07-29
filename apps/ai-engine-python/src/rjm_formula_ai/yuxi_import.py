import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


MOISTURIZING_KEYWORDS = {
    "moistur",
    "hydrat",
    "humectant",
    "barrier",
    "skin conditioning",
    "emollient",
    "保湿",
    "补水",
    "锁水",
    "屏障",
}


def import_yuxi_output(yuxi_output_dir: Path, output_dir: Path, limit: int | None = None) -> dict[str, Any]:
    ingredients = _read_moisturizing_ingredients(yuxi_output_dir / "ingredients_full.csv", limit)
    relations, product_evidence = _build_cooccurrence_relations(yuxi_output_dir / "products.json", ingredients)
    evidence = _build_evidence_catalog(ingredients, product_evidence)

    output_dir.mkdir(parents=True, exist_ok=True)
    ingredients_path = output_dir / "ingredients.yuxi.json"
    relations_path = output_dir / "ingredient_relations.yuxi.json"
    evidence_path = output_dir / "evidence.yuxi.json"
    batch_path = output_dir / "import_batch.yuxi.json"
    _write_json(ingredients_path, ingredients)
    _write_json(relations_path, relations)
    _write_json(evidence_path, evidence)
    _write_json(
        batch_path,
        _build_import_batch_record(
            yuxi_output_dir,
            ingredients_path,
            relations_path,
            evidence_path,
            len(ingredients),
            len(relations),
            len(evidence),
        ),
    )

    return {
        "ingredient_count": len(ingredients),
        "relation_count": len(relations),
        "evidence_count": len(evidence),
        "ingredients_path": str(ingredients_path),
        "relations_path": str(relations_path),
        "evidence_path": str(evidence_path),
        "batch_path": str(batch_path),
    }


def _read_moisturizing_ingredients(path: Path, limit: int | None) -> list[dict[str, Any]]:
    ingredients: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if not _is_moisturizing_row(row):
                continue
            ingredient_id = _ingredient_id(row["ingredient_name"])
            if ingredient_id in seen_ids:
                continue
            seen_ids.add(ingredient_id)
            ingredients.append(_ingredient_from_row(row, ingredient_id))
            if limit is not None and len(ingredients) >= limit:
                break
    return ingredients


def _is_moisturizing_row(row: dict[str, str]) -> bool:
    haystack = " ".join(
        [
            row.get("ingredient_name", ""),
            row.get("what_it_does", ""),
            row.get("all_functions", ""),
            row.get("description", ""),
        ]
    ).lower()
    return any(keyword.lower() in haystack for keyword in MOISTURIZING_KEYWORDS)


def _ingredient_from_row(row: dict[str, str], ingredient_id: str) -> dict[str, Any]:
    functions = _functions_from_row(row)
    return {
        "id": ingredient_id,
        "name_cn": row["ingredient_name"].strip(),
        "name_en": row["ingredient_name"].strip(),
        "inci_name": row["ingredient_name"].strip().upper(),
        "category": _category_from_functions(functions),
        "functions": functions,
        "properties": {
            "source": "yuxi-output",
            "ingredient_url": row.get("ingredient_url", ""),
            "what_it_does": row.get("what_it_does", ""),
            "all_functions": row.get("all_functions", ""),
            "cas_number": row.get("cas_number", ""),
            "description": row.get("description", ""),
        },
        "usage_range": {
            "min_percent": 0.1,
            "max_percent": 5.0,
            "typical_percent": 1.0,
        },
        "regulatory_limits": _split_text(row.get("sccs_opinions", "")),
        "risk_tags": [],
        "evidence_ids": [_ingredient_evidence_id(row["ingredient_name"])],
    }


def _functions_from_row(row: dict[str, str]) -> list[str]:
    raw_functions = _split_text(row.get("what_it_does", "")) + _split_text(row.get("all_functions", ""))
    functions = ["保湿"]
    for item in raw_functions:
        normalized = item.strip()
        if normalized and normalized.lower() not in {"moisturizer", "moisturizing"}:
            functions.append(normalized)
    return _dedupe(functions)


def _category_from_functions(functions: list[str]) -> str:
    lowered = {item.lower() for item in functions}
    if "humectant" in lowered:
        return "humectant"
    if "emollient" in lowered:
        return "emollient"
    if any("barrier" in item for item in lowered) or "屏障" in lowered:
        return "barrier_active"
    return "active"


def _build_cooccurrence_relations(
    products_path: Path,
    ingredients: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    id_by_url = {
        item["properties"]["ingredient_url"]: item["id"]
        for item in ingredients
        if item["properties"].get("ingredient_url")
    }
    if not id_by_url:
        return [], {}

    products = json.loads(products_path.read_text(encoding="utf-8"))
    pair_counts: Counter[tuple[str, str]] = Counter()
    evidence_by_pair: dict[tuple[str, str], set[str]] = {}
    product_evidence: dict[str, dict[str, Any]] = {}

    for product in products:
        product_ids = sorted(
            {
                id_by_url[ingredient["ingredient_url"]]
                for ingredient in product.get("ingredients", [])
                if ingredient.get("ingredient_url") in id_by_url
            }
        )
        if product_ids:
            evidence_id = _product_evidence_id(product.get("product_name", ""))
            product_evidence[evidence_id] = _product_evidence_from_product(product, product_ids, evidence_id)

        for source_id, target_id in combinations(product_ids, 2):
            pair = (source_id, target_id)
            pair_counts[pair] += 1
            evidence_by_pair.setdefault(pair, set()).add(_product_evidence_id(product.get("product_name", "")))

    relations = []
    for (source_id, target_id), count in sorted(pair_counts.items()):
        relations.append(
            {
                "id": f"REL-{source_id[4:]}-{target_id[4:]}-COOCCUR",
                "source_ingredient_id": source_id,
                "target_ingredient_id": target_id,
                "relation_type": "synergy",
                "description": "Yuxi 产品数据中共同出现，作为候选协同关系进入配方推荐图谱。",
                "strength": min(0.9, 0.45 + count * 0.05),
                "feedback_weight": 0.0,
                "evidence_ids": sorted(evidence_by_pair.get((source_id, target_id), set())),
            }
        )
    return relations, product_evidence


def _build_evidence_catalog(
    ingredients: list[dict[str, Any]],
    product_evidence: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    ingredient_evidence = [_ingredient_evidence_from_ingredient(item) for item in ingredients]
    return sorted(ingredient_evidence + list(product_evidence.values()), key=lambda item: item["id"])


def _ingredient_evidence_from_ingredient(ingredient: dict[str, Any]) -> dict[str, Any]:
    properties = ingredient.get("properties", {})
    summary = properties.get("description") or properties.get("what_it_does") or ingredient["name_en"]
    return {
        "id": ingredient["evidence_ids"][0],
        "source_type": "ingredient_profile",
        "title": ingredient["name_en"],
        "summary": summary[:500],
        "source_url": properties.get("ingredient_url", ""),
        "metadata": {
            "ingredient_id": ingredient["id"],
            "functions": ingredient["functions"],
            "cas_number": properties.get("cas_number", ""),
        },
    }


def _product_evidence_from_product(product: dict[str, Any], matched_ingredient_ids: list[str], evidence_id: str) -> dict[str, Any]:
    return {
        "id": evidence_id,
        "source_type": "product_cooccurrence",
        "title": product.get("product_name", ""),
        "summary": "Yuxi 产品配方中出现多个保湿相关原料，可作为候选共现证据。",
        "source_url": product.get("product_url", ""),
        "metadata": {
            "matched_ingredient_ids": matched_ingredient_ids,
            "ingredient_count": product.get("ingredient_count", len(product.get("ingredients", []))),
            "image_url": product.get("image_url", ""),
        },
    }


def _split_text(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,;/|]", value or "") if item.strip()]


def _ingredient_id(name: str) -> str:
    return "ING-" + _slug(name)


def _ingredient_evidence_id(name: str) -> str:
    return "YUXI-ING-" + _slug(name)


def _product_evidence_id(name: str) -> str:
    return "YUXI-PRODUCT-" + _slug(name or "UNKNOWN")


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.upper()).strip("-")
    return slug or "UNKNOWN"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _build_import_batch_record(
    yuxi_output_dir: Path,
    ingredients_path: Path,
    relations_path: Path,
    evidence_path: Path,
    ingredient_count: int,
    relation_count: int,
    evidence_count: int,
) -> dict[str, Any]:
    return {
        "batch_id": "YUXI-IMPORT-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {
            "ingredients_full_csv": str(yuxi_output_dir / "ingredients_full.csv"),
            "products_json": str(yuxi_output_dir / "products.json"),
        },
        "output_files": {
            "ingredients_path": str(ingredients_path),
            "relations_path": str(relations_path),
            "evidence_path": str(evidence_path),
        },
        "counts": {
            "ingredient_count": ingredient_count,
            "relation_count": relation_count,
            "evidence_count": evidence_count,
        },
        "governance_notes": [
            "Product co-occurrence relations are candidate graph hints.",
            "Evidence IDs should resolve through evidence.yuxi.json before recommendations cite them.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Yuxi output files into RJM formula AI JSON files.")
    parser.add_argument("--yuxi-output", type=Path, default=Path(r"F:\zky\Yuxi-main\output"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/yuxi_import"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    result = import_yuxi_output(args.yuxi_output, args.out_dir, args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
