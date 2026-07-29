# RJM Formula AI HTTP Service

## Status

The current API is a zero-dependency HTTP adapter built with Python standard library `http.server`.

FastAPI and uvicorn were not available in the current Python runtime, and installing them failed because the environment proxy was unavailable. The service layer is intentionally separated in `prototype/rjm_formula_ai/service.py` so a later FastAPI adapter can reuse the same business logic.

## Run

```powershell
cd F:\zky\RJM
$env:PYTHONPATH = "$PWD\prototype"
python -m rjm_formula_ai.http_server
```

Or:

```powershell
.\scripts\run_http_service.ps1
```

If PowerShell script execution is restricted, use the direct `python -m` command.

## Knowledge Source Overrides

By default the service loads the small moisturizing sample files under `data/samples`. Set these environment variables before startup to use generated or imported knowledge files:

```powershell
$env:RJM_INGREDIENTS_PATH = "$PWD\data\yuxi_import\ingredients.yuxi.json"
$env:RJM_RELATIONS_PATH = "$PWD\data\yuxi_import\ingredient_relations.yuxi.json"
$env:RJM_EVIDENCE_PATH = "$PWD\data\yuxi_import\evidence.yuxi.json"
$env:RJM_RAW_MATERIAL_SKUS_PATH = "$PWD\data\samples\raw_material_skus.json"
```

`RJM_FORMULA_PATH`, `RJM_FEEDBACK_PATH`, and `RJM_SCREENING_PATH` can also redirect runtime formula archives and event logs for smoke tests.

## Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Knowledge Status

```http
GET /knowledge/status
```

Response shape:

```json
{
  "ingredient_count": 46,
  "relation_count": 316,
  "raw_material_sku_count": 5,
  "evidence_count": 185,
  "source_paths": {
    "ingredients_path": "data/yuxi_import/ingredients.yuxi.json",
    "relations_path": "data/yuxi_import/ingredient_relations.yuxi.json",
    "evidence_path": "data/yuxi_import/evidence.yuxi.json"
  },
  "evidence_prefix_counts": {
    "YUXI": 46
  }
}
```

## Knowledge Governance

```http
GET /knowledge/governance
```

Response shape:

```json
{
  "ingredient_count": 46,
  "relation_count": 316,
  "evidence_source_type_counts": {
    "ingredient_profile": 46,
    "product_cooccurrence": 139
  },
  "relation_type_counts": {
    "synergy": 316
  },
  "relation_confidence_counts": {
    "medium": 316
  },
  "ingredient_alias_count": 0,
  "missing_evidence_ids": [],
  "warning_count": 1,
  "warnings": [
    "Yuxi product co-occurrence edges are recommendation hints, not lab-validated synergy."
  ],
  "governance_notes": [
    "Treat imported relation strength as prior confidence until experiment feedback adjusts it."
  ]
}
```

## Evidence Lookup

```http
GET /evidence/YUXI-ING-GLYCERIN
```

Response shape:

```json
{
  "id": "YUXI-ING-GLYCERIN",
  "source_type": "ingredient_profile",
  "title": "Glycerin",
  "summary": "Classic moisturizing ingredient.",
  "source_url": "https://incidecoder.com/ingredients/glycerin",
  "metadata": {
    "ingredient_id": "ING-GLYCERIN"
  }
}
```

## Recommend

```http
POST /recommend
Content-Type: application/json
```

Request:

```json
{
  "id": "REQ-MOIST-HTTP-001",
  "goal": "保湿",
  "dosage_form": "乳液",
  "constraints": {
    "preferred_skin_feel": "清爽不粘",
    "blocked_ingredient_ids": []
  }
}
```

Response shape:

```json
{
  "request_id": "REQ-MOIST-HTTP-001",
  "goal": "保湿",
  "formulas": []
}
```

## Feedback Recommend

Each `POST /recommend` and `POST /feedback/recommend` response is also appended to the formula candidate archive. The default archive path is `data/runtime/formula_candidates.jsonl`; override it with `RJM_FORMULA_PATH` when running smoke tests or isolated demos.

## Formula Archive Lookup

```http
GET /formulas/FORM-MOIST-001
```

Response shape:

```json
{
  "formula_id": "FORM-MOIST-001",
  "request_id": "REQ-MOIST-HTTP-001",
  "goal": "保湿",
  "stored_at": "2026-07-28T10:00:00Z",
  "formula": {
    "id": "FORM-MOIST-001",
    "ingredients": [],
    "score": {},
    "status": "candidate"
  }
}
```

If the formula has not been archived, the endpoint returns `404`.

```http
POST /feedback/recommend
Content-Type: application/json
```

Request:

```json
{
  "request": {
    "id": "REQ-MOIST-HTTP-001",
    "goal": "保湿",
    "dosage_form": "乳液",
    "constraints": {}
  },
  "feedback": [
    {
      "result": "pass",
      "ingredient_ids": ["ING-GLYCERIN", "ING-SODIUM-HYALURONATE"]
    }
  ]
}
```

Response shape:

```json
{
  "request_id": "REQ-MOIST-HTTP-001",
  "goal": "保湿",
  "formulas": []
}
```

## Record Feedback

```http
POST /feedback
Content-Type: application/json
```

This endpoint appends an experiment or engineer feedback event to `data/runtime/feedback_events.jsonl`. Future `POST /recommend` calls load this event log and apply feedback weights before ranking formulas.

Request:

```json
{
  "result": "pass",
  "ingredient_ids": ["ING-GLYCERIN", "ING-SODIUM-HYALURONATE"],
  "formula_id": "FORM-MOIST-001",
  "engineer_conclusion": "保湿效果可以，肤感略粘，下一轮降低甘油比例。"
}
```

Response:

```json
{
  "stored": true,
  "feedback_count": 1
}
```

## Procurement Recommend

```http
POST /procurement/recommend
Content-Type: application/json
```

Request:

```json
{
  "formula": {
    "id": "FORM-MOIST-001",
    "ingredients": [
      {
        "ingredient_id": "ING-GLYCERIN",
        "role": "基础保湿剂",
        "suggested_percent_min": 3.0,
        "suggested_percent_max": 5.0
      }
    ]
  }
}
```

Response shape:

```json
{
  "formula_id": "FORM-MOIST-001",
  "items": [
    {
      "ingredient_id": "ING-GLYCERIN",
      "status": "matched",
      "recommended_skus": [
        {
          "sku_id": "SKU-GLYCERIN-SUP-A",
          "supplier_id": "SUP-A",
          "specification": "化妆品级，99.5%",
          "price": {
            "currency": "CNY",
            "amount_per_kg": 12.5
          },
          "moq_kg": 25,
          "lead_time_days": 7,
          "qualification_files": ["COA", "MSDS"],
          "sample_status": "available",
          "quality_rating": 0.86,
          "procurement_score": 0.851
        }
      ]
    }
  ]
}
```

`items` are sorted with matched supplier records first. Ingredients without supplier records return `status: "missing_supplier"` and an empty `recommended_skus` list.

## Feedback Impact Report

```http
POST /reports/feedback-impact
Content-Type: application/json
```

Request:

```json
{
  "id": "REQ-FEEDBACK-REPORT",
  "goal": "保湿",
  "dosage_form": "乳液",
  "constraints": {}
}
```

Response shape:

```json
{
  "request_id": "REQ-FEEDBACK-REPORT",
  "goal": "保湿",
  "feedback_count": 0,
  "rows": [
    {
      "formula_id": "FORM-MOIST-001",
      "baseline_rank": 1,
      "learned_rank": 1,
      "baseline_score": 0.886,
      "learned_score": 0.936,
      "score_delta": 0.05,
      "ingredient_ids": ["ING-BETAINE", "ING-PANTHENOL"]
    }
  ]
}
```

## Record Engineer Screening

```http
POST /screening
Content-Type: application/json
```

This endpoint appends a formula engineer screening record to `data/runtime/screening_events.jsonl`.

Request:

```json
{
  "formula_id": "FORM-MOIST-001",
  "engineer": "formula_engineer",
  "decision": "keep",
  "reason": "保湿逻辑清楚，原料常见，适合进入小试。",
  "modified_ingredients": []
}
```

Response:

```json
{
  "stored": true,
  "screening_count": 1
}
```

## Query Engineer Screening

```http
GET /screening?formula_id=FORM-MOIST-001
```

Response:

```json
{
  "formula_id": "FORM-MOIST-001",
  "records": [
    {
      "formula_id": "FORM-MOIST-001",
      "engineer": "formula_engineer",
      "decision": "keep",
      "reason": "保湿逻辑清楚，原料常见，适合进入小试。",
      "modified_ingredients": []
    }
  ]
}
```

## Later FastAPI Adapter

Create `prototype/rjm_formula_ai/fastapi_app.py` only after dependencies are available. It should call:

- `FormulaAIService.from_project_root(project_root)`
- `FormulaAIService.recommend(request_payload)`
- `FormulaAIService.feedback_recommend(payload)`
- `FormulaAIService.recommend_procurement(payload)`
- `FormulaAIService.record_screening(payload)`
- `FormulaAIService.list_screening(formula_id)`
- `FormulaAIService.get_evidence(evidence_id)`
- `build_feedback_impact_report(service, request_payload)`
