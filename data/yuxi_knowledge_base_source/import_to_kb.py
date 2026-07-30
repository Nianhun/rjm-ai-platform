"""Validate extracted output data and import it into a Yuxi knowledge base.

The URL inventory in this directory is intentionally not imported. This script
builds a clean Markdown document from crawled product records and ingredient
notes, then uploads that document for parsing and indexing.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

API_BASE = os.getenv("YUXI_API_BASE", "http://localhost:5050/api")
KB_NAME = os.getenv("YUXI_KB_NAME", "Product Ingredient Knowledge")
EMBEDDING_MODEL_SPEC = os.getenv("YUXI_EMBEDDING_MODEL_SPEC", "siliconflow-cn:BAAI/bge-m3")

PRODUCTS_FILE = "products.ndjson"
INGREDIENTS_FILE = "ingredients_full.csv"
KNOWLEDGE_FILE = "products_knowledge.md"
ALLOWED_SOURCE_HOST = "incidecoder.com"

CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
URL_RE = re.compile(r"https?://\S+")
MOJIBAKE_MARKERS = ("鈥", "婼", "慽", "慸", "\ufffd")


def request_json(method: str, url: str, **kwargs: Any) -> Any:
    resp = requests.request(method, url, timeout=60, **kwargs)
    if resp.status_code >= 400:
        raise RuntimeError(f"{method} {url} failed: {resp.status_code} {resp.text}")
    return resp.json()


def clean_text(value: Any, max_length: int | None = None) -> str:
    text = " ".join(str(value or "").split())
    replacements = {
        "鈥婼": "S",
        "鈥婥": "C",
        "鈥": "",
        "\ufffd": "",
        "??": "",
        "?3": "-3",
        "\u200b": "",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = CONTROL_CHARS_RE.sub("", text).strip()
    if max_length and len(text) > max_length:
        return text[: max_length - 3].rstrip() + "..."
    return text


def source_key(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path.replace("/", ":") or "unknown"


def validate_source_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc == ALLOWED_SOURCE_HOST


def load_ingredient_notes(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}

    notes: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = clean_text(row.get("ingredient_name"))
            if not name:
                continue
            notes[name.lower()] = {
                "what_it_does": clean_text(row.get("what_it_does")),
                "all_functions": clean_text(row.get("all_functions")),
                "description": clean_text(row.get("description"), 600),
            }
    return notes


def iter_products(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                products.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSON at {path.name}:{line_no}: {exc}") from exc
            if limit and len(products) >= limit:
                break
    return products


def validate_output_data(output_dir: Path, limit: int | None = None) -> dict[str, int]:
    products_path = output_dir / PRODUCTS_FILE
    if not products_path.exists():
        raise FileNotFoundError(f"Missing {products_path}")

    products = iter_products(products_path, limit)
    if not products:
        raise RuntimeError(f"No products found in {products_path}")

    stats = {
        "products": 0,
        "ingredient_edges": 0,
        "products_without_name": 0,
        "products_without_ingredients": 0,
        "ingredients_without_name": 0,
        "invalid_source_urls": 0,
        "records_with_mojibake_markers": 0,
        "records_with_control_chars": 0,
    }

    for product in products:
        stats["products"] += 1
        name = clean_text(product.get("product_name"))
        if not name:
            stats["products_without_name"] += 1

        product_url = clean_text(product.get("product_url"))
        if product_url and not validate_source_url(product_url):
            stats["invalid_source_urls"] += 1

        ingredients = product.get("ingredients") or []
        if not ingredients:
            stats["products_without_ingredients"] += 1
        stats["ingredient_edges"] += len(ingredients)

        text = json.dumps(product, ensure_ascii=False)
        if any(marker in text for marker in MOJIBAKE_MARKERS):
            stats["records_with_mojibake_markers"] += 1
        if CONTROL_CHARS_RE.search(text):
            stats["records_with_control_chars"] += 1

        for ingredient in ingredients:
            if not clean_text(ingredient.get("ingredient_name")):
                stats["ingredients_without_name"] += 1
            ingredient_url = clean_text(ingredient.get("ingredient_url"))
            if ingredient_url and not validate_source_url(ingredient_url):
                stats["invalid_source_urls"] += 1

    blocking_errors = [
        "products_without_name",
        "products_without_ingredients",
        "ingredients_without_name",
        "invalid_source_urls",
        "records_with_control_chars",
    ]
    failed = {key: stats[key] for key in blocking_errors if stats[key]}
    if failed:
        raise RuntimeError(f"Output data failed validation: {failed}")

    return stats


def generate_knowledge_file(output_dir: Path, limit: int | None = None) -> Path:
    products = iter_products(output_dir / PRODUCTS_FILE, limit)
    ingredient_notes = load_ingredient_notes(output_dir / INGREDIENTS_FILE)
    target = output_dir / KNOWLEDGE_FILE

    lines = [
        "# Product Ingredient Knowledge",
        "",
        "This document is generated from extracted crawl records. Raw URL lists are not imported.",
        "Each product section keeps product entities and product-to-ingredient relationships for RAG and graph indexing.",
        "",
    ]

    used_ingredients: set[str] = set()
    for product in products:
        product_name = clean_text(product.get("product_name"))
        if not product_name:
            continue

        ingredients = product.get("ingredients") or []
        product_id = source_key(clean_text(product.get("product_url")))
        lines.extend(
            [
                f"## Product: {product_name}",
                "",
                "- Entity type: Product",
                f"- Product ID: {product_id}",
                f"- Status: {'Discontinued' if product.get('is_discontinued') else 'Active'}",
                f"- Ingredient count: {product.get('ingredient_count') or len(ingredients)}",
                "",
                "### Ingredient relationships",
                "",
            ]
        )

        for ingredient in ingredients:
            ingredient_name = clean_text(ingredient.get("ingredient_name"))
            if not ingredient_name:
                continue
            ingredient_id = source_key(clean_text(ingredient.get("ingredient_url")))
            used_ingredients.add(ingredient_name)
            lines.append(
                f"- Product {product_name} contains ingredient {ingredient_name}. "
                f"Ingredient ID: {ingredient_id}."
            )
        lines.append("")

    if ingredient_notes and used_ingredients:
        lines.extend(["# Ingredient Notes", ""])
        for ingredient_name in sorted(used_ingredients, key=str.lower):
            note = ingredient_notes.get(ingredient_name.lower())
            if not note:
                continue

            lines.extend([f"## Ingredient: {ingredient_name}", "", "- Entity type: Ingredient"])
            functions = note.get("what_it_does") or note.get("all_functions")
            if functions:
                lines.append(f"- Functions: {functions}")
            description = note.get("description")
            if description:
                lines.append(f"- Description: {description}")
            lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")

    content = target.read_text(encoding="utf-8", errors="replace")
    if URL_RE.search(content):
        raise RuntimeError(f"Generated {target.name} still contains raw URLs")
    if CONTROL_CHARS_RE.search(content):
        raise RuntimeError(f"Generated {target.name} contains control characters")

    print(f"  OK generated {target.name}: {len(products)} products, {target.stat().st_size} bytes")
    return target


def login() -> str:
    access_token = os.getenv("YUXI_ACCESS_TOKEN")
    if access_token:
        print("  OK using YUXI_ACCESS_TOKEN")
        return access_token

    username = os.getenv("YUXI_ADMIN_USERNAME") or os.getenv("ADMIN_USERNAME")
    password = os.getenv("YUXI_ADMIN_PASSWORD") or os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        raise RuntimeError(
            "Set YUXI_ADMIN_USERNAME/YUXI_ADMIN_PASSWORD or YUXI_ACCESS_TOKEN before importing"
        )

    data = request_json(
        "POST",
        f"{API_BASE}/auth/token",
        data={"username": username, "password": password},
    )
    print("  OK logged in")
    return data["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_or_create_kb(token: str) -> str:
    headers = auth_headers(token)
    data = request_json("GET", f"{API_BASE}/knowledge/databases", headers=headers)
    databases = data if isinstance(data, list) else data.get("databases", [])
    for db in databases:
        if db.get("name") == KB_NAME:
            kb_id = db["kb_id"]
            print(f"  OK using existing knowledge base {KB_NAME}: {kb_id}")
            return kb_id

    data = request_json(
        "POST",
        f"{API_BASE}/knowledge/databases",
        headers=headers,
        json={
            "database_name": KB_NAME,
            "description": "Generated from output/products.ndjson and output/ingredients_full.csv.",
            "kb_type": "milvus",
            "embedding_model_spec": EMBEDDING_MODEL_SPEC,
        },
    )
    kb_id = data["kb_id"]
    print(f"  OK created knowledge base {KB_NAME}: {kb_id}")
    return kb_id


def upload_file(token: str, kb_id: str, filepath: Path) -> tuple[str, str] | None:
    headers = auth_headers(token)
    with filepath.open("rb") as f:
        resp = requests.post(
            f"{API_BASE}/knowledge/files/upload",
            headers=headers,
            params={"kb_id": kb_id},
            files={"file": (filepath.name, f, "text/markdown")},
            timeout=120,
        )

    if resp.status_code == 409:
        print(f"  SKIP identical file already uploaded: {filepath.name}")
        return None
    if resp.status_code >= 400:
        raise RuntimeError(f"Upload failed for {filepath.name}: {resp.status_code} {resp.text}")

    result = resp.json()
    print(f"  OK uploaded {filepath.name}")
    return result["file_path"], result["content_hash"]


def add_document(token: str, kb_id: str, file_info: tuple[str, str] | None) -> str | None:
    if not file_info:
        return None

    minio_url, content_hash = file_info
    data = request_json(
        "POST",
        f"{API_BASE}/knowledge/databases/{kb_id}/documents",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={
            "items": [minio_url],
            "params": {
                "content_type": "file",
                "auto_index": True,
                "chunk_preset_id": "general",
                "content_hashes": {minio_url: content_hash},
            },
        },
    )
    task_id = data.get("task_id", "unknown")
    print(f"  OK submitted parse/index task: {task_id}")
    return task_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Import extracted output data into Yuxi KB")
    parser.add_argument("--limit", type=int, default=None, help="Import only the first N products")
    parser.add_argument("--dry-run", action="store_true", help="Validate and generate Markdown without uploading")
    args = parser.parse_args()

    output_dir = Path(__file__).resolve().parent

    print("Validating extracted output data...")
    stats = validate_output_data(output_dir, args.limit)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nGenerating clean knowledge document...")
    knowledge_file = generate_knowledge_file(output_dir, args.limit)

    if args.dry_run:
        print("\nDry run complete. No data was uploaded.")
        return

    print("\nLogging in...")
    token = login()

    print("\nCreating or finding target knowledge base...")
    kb_id = get_or_create_kb(token)

    print("\nUploading clean knowledge document...")
    uploaded = upload_file(token, kb_id, knowledge_file)

    print("\nSubmitting parse and index task...")
    task_id = add_document(token, kb_id, uploaded)

    time.sleep(0.2)
    print("\nImport submitted.")
    print(f"  KB: {KB_NAME} ({kb_id})")
    if task_id:
        print(f"  Task: {task_id}")
    print("  Web: http://localhost:5173")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        sys.exit(1)
