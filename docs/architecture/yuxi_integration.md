# Yuxi Integration Notes

## Purpose

Use Yuxi as the knowledge and graph base for RJM formula AI.

The RJM prototype in this workspace proves the formula recommendation loop with local JSON and Python. Yuxi should later provide document parsing, RAG retrieval, source evidence, graph extraction, and agent orchestration.

## Read First

- `F:\zky\Yuxi-main\README.md`
- `F:\zky\Yuxi-main\ARCHITECTURE.md`
- `F:\zky\Yuxi-main\docs\intro\knowledge-base.md`
- `F:\zky\Yuxi-main\docs\agents\agents-config.md`

## Knowledge Base Inputs

- 原料手册
- 配方实验记录
- 文献和专利资料
- 化妆品备案数据
- 供应商COA/MSDS资料

## Required Knowledge Tools

- Query knowledge base by 功效目标, 原料名称, INCI, 风险标签.
- Open source document chunk for evidence.
- Retrieve ingredient relation evidence.
- Write extracted structured facts to RJM prototype JSON first, then database later.

## Suggested Yuxi Knowledge Collections

| Collection | Purpose | Example Files |
| --- | --- | --- |
| `rjm-ingredients` | 原料属性、功效、用量、风险 | 原料手册、COA、MSDS |
| `rjm-literature` | 文献证据与配方机理 | 论文、综述、专利 |
| `rjm-experiments` | 配方实验反馈 | 实验记录、稳定性测试、肤感评价 |
| `rjm-suppliers` | 原料供应商证据 | 供应商资料、报价、资质文件 |

## Agent Integration Path

1. Use Yuxi document upload and parsing to ingest source files.
2. Use Yuxi RAG tools to retrieve source chunks for an ingredient or effect target.
3. Extract structured facts into the local `schemas/*.schema.json` format.
4. Store extracted facts as `data/samples/*.json` during prototype validation.
5. Once stable, replace local JSON files with database-backed services.
6. Keep formula recommendation output compatible with `formula_candidate.schema.json`.

## Current Import Adapter

RJM now includes a read-only adapter for Yuxi exported files:

```powershell
cd F:\zky\RJM
.\scripts\run_yuxi_import.ps1
```

The adapter reads:

- `F:\zky\Yuxi-main\output\ingredients_full.csv`
- `F:\zky\Yuxi-main\output\products.json`

It writes:

- `data/yuxi_import/ingredients.yuxi.json`
- `data/yuxi_import/ingredient_relations.yuxi.json`
- `data/yuxi_import/evidence.yuxi.json`

The first import path filters moisturizing-related ingredients by function and description keywords. Relation edges are built from product co-occurrence and are labeled as candidate `synergy` edges with Yuxi product evidence IDs. Treat these edges as recommendation hints, not validated lab synergy.

`evidence.yuxi.json` is a temporary traceability catalog. Each record includes `id`, `source_type`, `title`, `summary`, `source_url`, and `metadata`. This gives the Java management system and engineer console a stable lookup path before the project calls Yuxi RAG/KG services directly.

To run the Python AI service on imported Yuxi knowledge:

```powershell
cd F:\zky\RJM
$env:PYTHONPATH = "$PWD\prototype"
$env:RJM_INGREDIENTS_PATH = "$PWD\data\yuxi_import\ingredients.yuxi.json"
$env:RJM_RELATIONS_PATH = "$PWD\data\yuxi_import\ingredient_relations.yuxi.json"
$env:RJM_EVIDENCE_PATH = "$PWD\data\yuxi_import\evidence.yuxi.json"
python -m rjm_formula_ai.http_server
```

The same environment variables work with Java `python` mode because Java calls the Python HTTP service through the existing API boundary.

## Do Not

- Do not overwrite existing Yuxi knowledge base data.
- Do not change Yuxi deployment configuration without a separate task.
- Do not expose private MinIO files publicly.
- Do not treat AI-generated formula candidates as approved formulas.
- Do not skip engineer screening or experiment feedback records.

## Integration Acceptance

- A later Agent can retrieve evidence for at least one moisturizing ingredient from Yuxi.
- The retrieved evidence can be converted into an `Ingredient` or `IngredientRelation` JSON object.
- A formula recommendation can cite evidence IDs that trace back to Yuxi source chunks.
- The local CLI demo still runs after Yuxi integration notes are added.
