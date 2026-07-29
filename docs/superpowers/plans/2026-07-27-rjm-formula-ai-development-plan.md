# 瑞吉明配方AI系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建设一个一人公司可逐步落地的配方AI系统：用户提出功效目标，例如“保湿配方”，AI基于原料知识图谱输出配方推荐List，配方工程师筛选后开展实验，实验反馈反向更新推荐权重，并衔接原料供应商采购。

**Architecture:** 第一阶段不重写Yuxi，而是复用 `F:\zky\Yuxi-main` 作为知识库、RAG、图谱和Agent底座；在 `F:\zky\RJM` 维护项目管理、原型代码、数据Schema、测试样例和交接文档。Python先实现配方推荐闭环原型，Java管理系统后置承接用户、任务、实验、采购和供应商流程。

**Tech Stack:** Python 3.11+、Yuxi、Milvus、Neo4j、PostgreSQL、MinIO、LangGraph、FastAPI、pytest、JSON Schema；后续Java采用 Spring Boot 3、PostgreSQL、OpenAPI。

## Global Constraints

- 一人公司节奏：每个任务必须在 0.5-2 天内形成可运行、可测试、可交接的结果。
- 第一版只做配方推荐和反馈学习闭环，不做真实工厂设备控制。
- AI输出不得作为最终配方结论，必须保留证据链、推荐理由、风险提示、工程师筛选状态和实验反馈。
- 所有原料、配方、实验、供应商对象必须有稳定ID，便于跨系统追踪。
- 所有任务必须优先产出可被后续Agent读取的 Markdown、JSON Schema、测试样例或Python模块。
- 不改动 `F:\zky\Yuxi-main` 中已完成的知识库搭建，除非执行任务明确要求并先备份说明。
- 文档、样例和原型代码统一放在 `F:\zky\RJM` 下。
- 每个实现任务完成后必须更新 `docs/agent_handoff.md`，记录已完成内容、验证命令、下一步入口。

---

## 0. 一人公司项目管理规则

### 工作节奏

- 每天只推进一个主任务，避免同时开多个大模块。
- 每个任务结束必须留下三个东西：代码或文档产物、验证结果、下一步建议。
- 每周五做一次复盘：保留有效任务，砍掉暂时不影响闭环的功能。
- 第一阶段的唯一主线是“保湿配方推荐List -> 工程师筛选 -> 实验反馈 -> 推荐进化 -> 原料供应商采购”。

### 后续Agent启动方式

后续Agent进入项目后，先按顺序读取：

1. `F:\zky\RJM\docs\superpowers\plans\2026-07-27-rjm-formula-ai-development-plan.md`
2. `F:\zky\RJM\瑞吉明生物医药AI智能系统详细设计文档.docx`
3. `F:\zky\RJM\docs\agent_handoff.md`
4. `F:\zky\RJM\schemas\*.schema.json`
5. `F:\zky\RJM\prototype\README.md`

### 完成定义

一个任务只有满足以下条件才算完成：

- 有明确文件变更。
- 有可运行命令。
- 命令输出符合预期。
- 有测试样例或人工验收步骤。
- `docs/agent_handoff.md` 已更新。

---

## 1. 目标MVP范围

### MVP必须实现

- 原料主数据Schema：名称、INCI、功效、属性、风险、用量范围、法规限制。
- 原料关系Schema：协同、冲突、替代、增强、禁忌、供应关系。
- 配方推荐输入Schema：功效目标、剂型、成本、肤感、禁用原料、法规约束。
- 配方推荐输出Schema：配方List、原料比例范围、推荐理由、证据链、风险、评分。
- 工程师筛选Schema：保留、剔除、修改、备注、原因。
- 实验反馈Schema：稳定性、肤感、功效、成本、异常、结论。
- 反馈学习原型：根据实验成功/失败调整原料关系权重和配方推荐分数。
- 原料供应商采购Schema：供应商、规格、价格、MOQ、交期、COA、样品状态。
- 一个保湿配方端到端演示：输入“做一个保湿配方”，输出候选配方，筛选后写入实验反馈，再生成更新后的推荐排序。

### MVP明确不做

- 不做真实设备自动控制。
- 不做完整Java后台。
- 不做复杂数字孪生。
- 不做模型微调。
- 不做国家局备案接口真实联调。
- 不做供应商真实账号体系。

---

## 2. 建议目录结构

在 `F:\zky\RJM` 下建立以下结构：

```text
F:\zky\RJM
├── docs
│   ├── agent_handoff.md
│   ├── product_brief.md
│   ├── architecture_decisions.md
│   └── superpowers
│       └── plans
│           └── 2026-07-27-rjm-formula-ai-development-plan.md
├── schemas
│   ├── ingredient.schema.json
│   ├── ingredient_relation.schema.json
│   ├── formula_request.schema.json
│   ├── formula_candidate.schema.json
│   ├── formula_screening.schema.json
│   ├── experiment_feedback.schema.json
│   └── raw_material_sku.schema.json
├── data
│   ├── samples
│   │   ├── ingredients.moisturizing.json
│   │   ├── ingredient_relations.moisturizing.json
│   │   ├── formula_requests.json
│   │   ├── experiment_feedback.json
│   │   └── raw_material_skus.json
│   └── outputs
│       ├── formula_recommendations.before_feedback.json
│       └── formula_recommendations.after_feedback.json
├── prototype
│   ├── README.md
│   ├── rjm_formula_ai
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── load_data.py
│   │   ├── recommend.py
│   │   ├── feedback.py
│   │   └── cli.py
│   └── tests
│       ├── test_schema_examples.py
│       ├── test_recommendation.py
│       └── test_feedback_learning.py
└── scripts
    └── run_formula_demo.ps1
```

---

## 3. 数据契约

### Ingredient

```json
{
  "id": "ING-GLYCERIN",
  "name_cn": "甘油",
  "name_en": "Glycerin",
  "inci_name": "GLYCERIN",
  "category": "humectant",
  "functions": ["保湿", "溶剂"],
  "properties": {
    "water_soluble": true,
    "oil_soluble": false,
    "skin_feel": "略粘",
    "ph_range": "3.0-10.0"
  },
  "usage_range": {
    "min_percent": 1.0,
    "max_percent": 10.0,
    "typical_percent": 5.0
  },
  "regulatory_limits": [],
  "risk_tags": ["高用量可能粘腻"],
  "evidence_ids": ["DOC-MOIST-001"]
}
```

### IngredientRelation

```json
{
  "id": "REL-GLYCERIN-HA-SYNERGY",
  "source_ingredient_id": "ING-GLYCERIN",
  "target_ingredient_id": "ING-SODIUM-HYALURONATE",
  "relation_type": "synergy",
  "description": "甘油提供基础吸湿，透明质酸钠提升长效保水感。",
  "strength": 0.72,
  "feedback_weight": 0.0,
  "evidence_ids": ["DOC-MOIST-001", "EXP-MOIST-001"]
}
```

### FormulaRequest

```json
{
  "id": "REQ-MOIST-001",
  "goal": "保湿",
  "dosage_form": "乳液",
  "constraints": {
    "max_cost_level": "medium",
    "preferred_skin_feel": "清爽不粘",
    "blocked_ingredient_ids": [],
    "required_claims": ["长效保湿", "屏障修护"],
    "market": "中国"
  }
}
```

### FormulaCandidate

```json
{
  "id": "FORM-MOIST-001",
  "request_id": "REQ-MOIST-001",
  "goal": "保湿",
  "ingredients": [
    {
      "ingredient_id": "ING-GLYCERIN",
      "role": "基础保湿剂",
      "suggested_percent_min": 3.0,
      "suggested_percent_max": 5.0
    }
  ],
  "recommendation_reason": "甘油提供基础吸湿能力，透明质酸钠增强长效保水，泛醇补充舒缓和屏障修护。",
  "risk_notes": ["甘油过高可能粘腻，建议控制在5%以内。"],
  "evidence_ids": ["DOC-MOIST-001", "REL-GLYCERIN-HA-SYNERGY"],
  "score": {
    "efficacy": 0.82,
    "stability": 0.74,
    "skin_feel": 0.68,
    "cost": 0.76,
    "supply": 0.80,
    "overall": 0.77
  },
  "status": "ai_recommended"
}
```

### FormulaScreening

```json
{
  "id": "SCREEN-FORM-MOIST-001",
  "formula_id": "FORM-MOIST-001",
  "engineer": "formula_engineer",
  "decision": "keep",
  "modified_ingredients": [],
  "reason": "保湿逻辑清晰，原料常见，成本可控，适合小试。",
  "created_at": "2026-07-27T10:00:00+08:00"
}
```

### ExperimentFeedback

```json
{
  "id": "EXP-MOIST-001",
  "formula_id": "FORM-MOIST-001",
  "batch_no": "BATCH-MOIST-001",
  "result": "pass",
  "metrics": {
    "stability": "pass",
    "skin_feel": "slightly_sticky",
    "moisturizing_score": 0.84,
    "cost_level": "medium"
  },
  "issues": ["肤感略粘"],
  "engineer_conclusion": "保湿效果可以，建议降低甘油或增加清爽肤感调节原料。",
  "created_at": "2026-07-27T16:00:00+08:00"
}
```

### RawMaterialSku

```json
{
  "id": "SKU-GLYCERIN-SUP-A",
  "ingredient_id": "ING-GLYCERIN",
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
  "quality_rating": 0.86
}
```

---

## 4. Agent工作分工

### Knowledge Agent

职责：

- 读取文献、专利、原料资料。
- 抽取原料属性、功效、用量、风险和证据。
- 写入 `Ingredient` 和 `IngredientRelation`。

输入：

- 文献PDF、DOCX、Markdown、原料手册、备案数据。

输出：

- `schemas/ingredient.schema.json` 兼容的原料数据。
- `schemas/ingredient_relation.schema.json` 兼容的关系数据。

### Formula Recommendation Agent

职责：

- 接收功效目标，例如“保湿”。
- 从原料图谱中召回候选原料。
- 根据功效、相容性、风险、成本、供应链可得性和历史反馈生成配方List。

输出要求：

- 至少3套候选配方。
- 每套配方必须包含原料角色、建议比例范围、推荐理由、风险提示、证据链和综合评分。

### Engineer Screening Agent

职责：

- 辅助工程师记录筛选结果。
- 将保留、剔除、修改原因结构化。
- 不替代工程师决策。

### Experiment Feedback Agent

职责：

- 接收实验反馈。
- 识别成功、失败、异常和改进建议。
- 更新原料关系 `feedback_weight` 和候选配方评分。

### Procurement Agent

职责：

- 对通过实验的配方匹配原料供应商。
- 按价格、交期、资质、样品状态和质量评分排序。
- 输出采购建议。

---

## 5. 实施任务

### Task 1: 建立项目交接文档与目录骨架

**Files:**
- Create: `docs/agent_handoff.md`
- Create: `docs/product_brief.md`
- Create: `docs/architecture_decisions.md`
- Create: `schemas/.gitkeep`
- Create: `data/samples/.gitkeep`
- Create: `data/outputs/.gitkeep`
- Create: `prototype/README.md`

**Interfaces:**
- Consumes: 本计划文档。
- Produces: 后续Agent固定读取入口 `docs/agent_handoff.md`。

- [ ] **Step 1: Create directories**

Run:

```powershell
New-Item -ItemType Directory -Force docs,schemas,data\samples,data\outputs,prototype
```

Expected: directories exist under `F:\zky\RJM`.

- [ ] **Step 2: Create handoff document**

Create `docs/agent_handoff.md`:

```markdown
# Agent Handoff

## Current Status

- Project stage: planning and Python prototype preparation.
- Main goal: build moisturizing formula recommendation loop.
- Latest completed task: Task 1 project skeleton.

## How To Resume

1. Read `docs/superpowers/plans/2026-07-27-rjm-formula-ai-development-plan.md`.
2. Read this file.
3. Run the latest verification command listed below.
4. Continue with the next unchecked task.

## Verification Log

| Date | Command | Expected | Result |
| --- | --- | --- | --- |
| 2026-07-27 | `Get-ChildItem docs,schemas,data,prototype` | directories exist | pending |

## Next Task

Task 2: Create JSON Schemas.
```

- [ ] **Step 3: Create product brief**

Create `docs/product_brief.md`:

```markdown
# Product Brief

## Product

瑞吉明配方AI系统。

## Primary Scenario

配方工程师输入“我要一个保湿配方”，系统基于原料知识图谱、原料属性、历史实验反馈和供应商数据，输出可解释的配方推荐List。工程师筛选后开展实验，实验结果反馈系统，系统更新推荐权重。通过实验的配方进入原料供应商匹配和采购流程。

## MVP Success

- AI能输出至少3套保湿候选配方。
- 每套候选配方有证据链、风险提示和推荐评分。
- 工程师可以记录保留或剔除原因。
- 实验反馈能改变下一次推荐排序。
- 可行配方能匹配原料供应商。
```

- [ ] **Step 4: Create architecture decisions**

Create `docs/architecture_decisions.md`:

```markdown
# Architecture Decisions

## ADR-001: Use Yuxi as knowledge and agent base

Decision: Reuse `F:\zky\Yuxi-main` for knowledge base, RAG, graph, and agent orchestration.

Reason: Yuxi already provides document parsing, Milvus retrieval, Neo4j graph support, and LangGraph agents.

Consequence: RJM-specific prototype code stays in `F:\zky\RJM`; Yuxi changes require explicit task approval.

## ADR-002: Use Python before Java

Decision: Build the formula recommendation loop in Python first.

Reason: The core uncertainty is AI extraction, recommendation, and feedback learning, not enterprise CRUD.

Consequence: Java management system starts after the Python loop proves value.

## ADR-003: Keep human approval in the loop

Decision: Formula recommendations are draft references for engineers.

Reason: Cosmetic and biomedical formulation decisions require expert review, experiment, and compliance checks.

Consequence: Every formula candidate has a status and screening record.
```

- [ ] **Step 5: Verify**

Run:

```powershell
Get-ChildItem docs,schemas,data,prototype
```

Expected: all directories and three docs exist.

- [ ] **Step 6: Commit**

Run:

```bash
git add docs schemas data prototype
git commit -m "docs: add rjm formula ai project skeleton"
```

Expected: commit succeeds if repository is initialized.

---

### Task 2: Create JSON Schemas

**Files:**
- Create: `schemas/ingredient.schema.json`
- Create: `schemas/ingredient_relation.schema.json`
- Create: `schemas/formula_request.schema.json`
- Create: `schemas/formula_candidate.schema.json`
- Create: `schemas/formula_screening.schema.json`
- Create: `schemas/experiment_feedback.schema.json`
- Create: `schemas/raw_material_sku.schema.json`
- Modify: `docs/agent_handoff.md`

**Interfaces:**
- Consumes: data contracts in section 3.
- Produces: JSON Schema files used by sample validation and prototype loaders.

- [ ] **Step 1: Create `ingredient.schema.json`**

Use this schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Ingredient",
  "type": "object",
  "required": ["id", "name_cn", "inci_name", "category", "functions", "properties", "usage_range", "risk_tags", "evidence_ids"],
  "properties": {
    "id": {"type": "string", "pattern": "^ING-[A-Z0-9-]+$"},
    "name_cn": {"type": "string", "minLength": 1},
    "name_en": {"type": "string"},
    "inci_name": {"type": "string", "minLength": 1},
    "category": {"type": "string"},
    "functions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "properties": {"type": "object"},
    "usage_range": {
      "type": "object",
      "required": ["min_percent", "max_percent", "typical_percent"],
      "properties": {
        "min_percent": {"type": "number", "minimum": 0},
        "max_percent": {"type": "number", "minimum": 0},
        "typical_percent": {"type": "number", "minimum": 0}
      }
    },
    "regulatory_limits": {"type": "array", "items": {"type": "string"}},
    "risk_tags": {"type": "array", "items": {"type": "string"}},
    "evidence_ids": {"type": "array", "items": {"type": "string"}}
  }
}
```

- [ ] **Step 2: Create remaining schemas**

Create the other schema files using the example objects in section 3 as the required shape. Required fields:

- `ingredient_relation.schema.json`: `id`, `source_ingredient_id`, `target_ingredient_id`, `relation_type`, `strength`, `feedback_weight`, `evidence_ids`.
- `formula_request.schema.json`: `id`, `goal`, `dosage_form`, `constraints`.
- `formula_candidate.schema.json`: `id`, `request_id`, `goal`, `ingredients`, `recommendation_reason`, `risk_notes`, `evidence_ids`, `score`, `status`.
- `formula_screening.schema.json`: `id`, `formula_id`, `engineer`, `decision`, `reason`, `created_at`.
- `experiment_feedback.schema.json`: `id`, `formula_id`, `batch_no`, `result`, `metrics`, `issues`, `engineer_conclusion`, `created_at`.
- `raw_material_sku.schema.json`: `id`, `ingredient_id`, `supplier_id`, `specification`, `price`, `moq_kg`, `lead_time_days`, `qualification_files`, `sample_status`, `quality_rating`.

- [ ] **Step 3: Verify schemas parse**

Run:

```powershell
python -m json.tool schemas\ingredient.schema.json
```

Expected: formatted JSON prints without parse errors.

- [ ] **Step 4: Update handoff**

Append to `docs/agent_handoff.md`:

```markdown

## Task 2 Notes

- JSON Schemas created under `schemas/`.
- Next task: create moisturizing sample data and validate against schemas.
```

- [ ] **Step 5: Commit**

Run:

```bash
git add schemas docs/agent_handoff.md
git commit -m "docs: define formula ai json schemas"
```

Expected: commit succeeds if repository is initialized.

---

### Task 3: Create Moisturizing Sample Data

**Files:**
- Create: `data/samples/ingredients.moisturizing.json`
- Create: `data/samples/ingredient_relations.moisturizing.json`
- Create: `data/samples/formula_requests.json`
- Create: `data/samples/experiment_feedback.json`
- Create: `data/samples/raw_material_skus.json`
- Modify: `docs/agent_handoff.md`

**Interfaces:**
- Consumes: JSON Schemas from Task 2.
- Produces: stable sample data for prototype tests.

- [ ] **Step 1: Create moisturizing ingredients**

Create `data/samples/ingredients.moisturizing.json` with at least these ingredients:

```json
[
  {
    "id": "ING-GLYCERIN",
    "name_cn": "甘油",
    "name_en": "Glycerin",
    "inci_name": "GLYCERIN",
    "category": "humectant",
    "functions": ["保湿", "溶剂"],
    "properties": {"water_soluble": true, "skin_feel": "略粘"},
    "usage_range": {"min_percent": 1.0, "max_percent": 10.0, "typical_percent": 5.0},
    "regulatory_limits": [],
    "risk_tags": ["高用量可能粘腻"],
    "evidence_ids": ["DOC-MOIST-001"]
  },
  {
    "id": "ING-SODIUM-HYALURONATE",
    "name_cn": "透明质酸钠",
    "name_en": "Sodium Hyaluronate",
    "inci_name": "SODIUM HYALURONATE",
    "category": "humectant",
    "functions": ["保湿", "长效锁水"],
    "properties": {"water_soluble": true, "skin_feel": "润滑"},
    "usage_range": {"min_percent": 0.01, "max_percent": 0.3, "typical_percent": 0.1},
    "regulatory_limits": [],
    "risk_tags": ["高分子量体系需关注溶解和肤感"],
    "evidence_ids": ["DOC-MOIST-002"]
  },
  {
    "id": "ING-PANTHENOL",
    "name_cn": "泛醇",
    "name_en": "Panthenol",
    "inci_name": "PANTHENOL",
    "category": "active",
    "functions": ["保湿", "舒缓", "屏障修护"],
    "properties": {"water_soluble": true, "skin_feel": "柔润"},
    "usage_range": {"min_percent": 0.5, "max_percent": 5.0, "typical_percent": 2.0},
    "regulatory_limits": [],
    "risk_tags": [],
    "evidence_ids": ["DOC-MOIST-003"]
  },
  {
    "id": "ING-BETAINE",
    "name_cn": "甜菜碱",
    "name_en": "Betaine",
    "inci_name": "BETAINE",
    "category": "humectant",
    "functions": ["保湿", "降低刺激感"],
    "properties": {"water_soluble": true, "skin_feel": "清爽"},
    "usage_range": {"min_percent": 1.0, "max_percent": 5.0, "typical_percent": 3.0},
    "regulatory_limits": [],
    "risk_tags": [],
    "evidence_ids": ["DOC-MOIST-004"]
  }
]
```

- [ ] **Step 2: Create relations**

Create `data/samples/ingredient_relations.moisturizing.json`:

```json
[
  {
    "id": "REL-GLYCERIN-HA-SYNERGY",
    "source_ingredient_id": "ING-GLYCERIN",
    "target_ingredient_id": "ING-SODIUM-HYALURONATE",
    "relation_type": "synergy",
    "description": "基础吸湿与长效保水组合。",
    "strength": 0.72,
    "feedback_weight": 0.0,
    "evidence_ids": ["DOC-MOIST-001"]
  },
  {
    "id": "REL-PANTHENOL-BETAINE-SYNERGY",
    "source_ingredient_id": "ING-PANTHENOL",
    "target_ingredient_id": "ING-BETAINE",
    "relation_type": "synergy",
    "description": "舒缓修护与清爽保湿组合。",
    "strength": 0.68,
    "feedback_weight": 0.0,
    "evidence_ids": ["DOC-MOIST-004"]
  }
]
```

- [ ] **Step 3: Create request and feedback samples**

Create a request for `REQ-MOIST-001` and one feedback record for `FORM-MOIST-001` using the examples in section 3.

- [ ] **Step 4: Verify JSON parses**

Run:

```powershell
python -m json.tool data\samples\ingredients.moisturizing.json
python -m json.tool data\samples\ingredient_relations.moisturizing.json
```

Expected: both files print formatted JSON without parse errors.

- [ ] **Step 5: Update handoff and commit**

Append:

```markdown

## Task 3 Notes

- Moisturizing sample data created.
- Next task: implement Python prototype models and loader.
```

Commit:

```bash
git add data docs/agent_handoff.md
git commit -m "testdata: add moisturizing formula samples"
```

---

### Task 4: Implement Python Models and Data Loader

**Files:**
- Create: `prototype/rjm_formula_ai/__init__.py`
- Create: `prototype/rjm_formula_ai/models.py`
- Create: `prototype/rjm_formula_ai/load_data.py`
- Create: `prototype/tests/test_schema_examples.py`
- Modify: `prototype/README.md`
- Modify: `docs/agent_handoff.md`

**Interfaces:**
- Consumes: sample JSON from Task 3.
- Produces:
  - `load_ingredients(path: Path) -> list[Ingredient]`
  - `load_relations(path: Path) -> list[IngredientRelation]`
  - `load_formula_requests(path: Path) -> list[FormulaRequest]`

- [ ] **Step 1: Write failing tests**

Create `prototype/tests/test_schema_examples.py`:

```python
from pathlib import Path

from rjm_formula_ai.load_data import load_ingredients, load_relations


ROOT = Path(__file__).resolve().parents[2]


def test_load_moisturizing_ingredients():
    ingredients = load_ingredients(ROOT / "data" / "samples" / "ingredients.moisturizing.json")
    assert len(ingredients) >= 4
    assert ingredients[0].id.startswith("ING-")
    assert any("保湿" in item.functions for item in ingredients)


def test_load_moisturizing_relations():
    relations = load_relations(ROOT / "data" / "samples" / "ingredient_relations.moisturizing.json")
    assert len(relations) >= 2
    assert relations[0].relation_type in {"synergy", "conflict", "substitute", "risk"}
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd prototype
python -m pytest tests\test_schema_examples.py -v
```

Expected: FAIL because `rjm_formula_ai` does not exist.

- [ ] **Step 3: Implement models**

Create `prototype/rjm_formula_ai/models.py`:

```python
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
```

- [ ] **Step 4: Implement loader**

Create `prototype/rjm_formula_ai/load_data.py`:

```python
import json
from pathlib import Path
from typing import Any

from .models import FormulaRequest, Ingredient, IngredientRelation, UsageRange


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_ingredients(path: Path) -> list[Ingredient]:
    rows = _read_json(path)
    return [
        Ingredient(
            id=row["id"],
            name_cn=row["name_cn"],
            name_en=row.get("name_en", ""),
            inci_name=row["inci_name"],
            category=row["category"],
            functions=list(row["functions"]),
            properties=dict(row["properties"]),
            usage_range=UsageRange(**row["usage_range"]),
            regulatory_limits=list(row.get("regulatory_limits", [])),
            risk_tags=list(row.get("risk_tags", [])),
            evidence_ids=list(row.get("evidence_ids", [])),
        )
        for row in rows
    ]


def load_relations(path: Path) -> list[IngredientRelation]:
    rows = _read_json(path)
    return [IngredientRelation(**row) for row in rows]


def load_formula_requests(path: Path) -> list[FormulaRequest]:
    rows = _read_json(path)
    return [FormulaRequest(**row) for row in rows]
```

- [ ] **Step 5: Add package init**

Create `prototype/rjm_formula_ai/__init__.py`:

```python
"""RJM formula AI prototype."""
```

- [ ] **Step 6: Run tests**

Run:

```powershell
cd prototype
python -m pytest tests\test_schema_examples.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```bash
git add prototype docs/agent_handoff.md
git commit -m "feat: load formula ai sample data"
```

---

### Task 5: Implement Formula Recommendation Prototype

**Files:**
- Create: `prototype/rjm_formula_ai/recommend.py`
- Create: `prototype/tests/test_recommendation.py`
- Modify: `docs/agent_handoff.md`

**Interfaces:**
- Consumes:
  - `Ingredient`
  - `IngredientRelation`
  - `FormulaRequest`
- Produces:
  - `recommend_formulas(request, ingredients, relations, limit=3) -> list[dict]`

- [ ] **Step 1: Write failing recommendation test**

Create `prototype/tests/test_recommendation.py`:

```python
from pathlib import Path

from rjm_formula_ai.load_data import load_formula_requests, load_ingredients, load_relations
from rjm_formula_ai.recommend import recommend_formulas


ROOT = Path(__file__).resolve().parents[2]


def test_recommend_moisturizing_formulas():
    ingredients = load_ingredients(ROOT / "data" / "samples" / "ingredients.moisturizing.json")
    relations = load_relations(ROOT / "data" / "samples" / "ingredient_relations.moisturizing.json")
    request = load_formula_requests(ROOT / "data" / "samples" / "formula_requests.json")[0]

    formulas = recommend_formulas(request, ingredients, relations, limit=3)

    assert len(formulas) == 3
    assert formulas[0]["goal"] == "保湿"
    assert formulas[0]["score"]["overall"] > 0
    assert formulas[0]["ingredients"]
    assert formulas[0]["recommendation_reason"]
    assert formulas[0]["risk_notes"] is not None
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
cd prototype
python -m pytest tests\test_recommendation.py -v
```

Expected: FAIL because `recommend.py` does not exist.

- [ ] **Step 3: Implement simple recommendation algorithm**

Create `prototype/rjm_formula_ai/recommend.py`:

```python
from .models import FormulaRequest, Ingredient, IngredientRelation


def _goal_match_score(goal: str, ingredient: Ingredient) -> float:
    return 1.0 if goal in ingredient.functions else 0.35


def _relation_bonus(ingredient_ids: set[str], relations: list[IngredientRelation]) -> float:
    bonus = 0.0
    for relation in relations:
        if relation.source_ingredient_id in ingredient_ids and relation.target_ingredient_id in ingredient_ids:
            if relation.relation_type == "synergy":
                bonus += relation.strength + relation.feedback_weight
            if relation.relation_type in {"conflict", "risk"}:
                bonus -= relation.strength
    return bonus


def recommend_formulas(
    request: FormulaRequest,
    ingredients: list[Ingredient],
    relations: list[IngredientRelation],
    limit: int = 3,
) -> list[dict]:
    ranked = sorted(
        ingredients,
        key=lambda item: (_goal_match_score(request.goal, item), item.usage_range.typical_percent),
        reverse=True,
    )
    base_pool = ranked[: max(4, min(len(ranked), 6))]
    formulas: list[dict] = []

    windows = [
        base_pool[:3],
        base_pool[1:4],
        [base_pool[0], base_pool[2], base_pool[3]] if len(base_pool) >= 4 else base_pool[:3],
    ]

    for index, selected in enumerate(windows[:limit], start=1):
        ids = {item.id for item in selected}
        efficacy = sum(_goal_match_score(request.goal, item) for item in selected) / len(selected)
        relation = _relation_bonus(ids, relations)
        skin_feel_penalty = 0.08 if any("粘" in tag for item in selected for tag in item.risk_tags) else 0.0
        overall = max(0.0, min(1.0, 0.55 * efficacy + 0.20 * relation + 0.20 - skin_feel_penalty))

        formulas.append(
            {
                "id": f"FORM-{request.goal.upper()}-{index:03d}",
                "request_id": request.id,
                "goal": request.goal,
                "ingredients": [
                    {
                        "ingredient_id": item.id,
                        "role": "功效/辅助原料",
                        "suggested_percent_min": item.usage_range.min_percent,
                        "suggested_percent_max": item.usage_range.typical_percent,
                    }
                    for item in selected
                ],
                "recommendation_reason": "基于功效匹配、原料协同关系、风险标签和基础用量范围生成。",
                "risk_notes": [tag for item in selected for tag in item.risk_tags],
                "evidence_ids": sorted({eid for item in selected for eid in item.evidence_ids}),
                "score": {
                    "efficacy": round(efficacy, 3),
                    "stability": 0.7,
                    "skin_feel": round(0.8 - skin_feel_penalty, 3),
                    "cost": 0.75,
                    "supply": 0.75,
                    "overall": round(overall, 3),
                },
                "status": "ai_recommended",
            }
        )

    return sorted(formulas, key=lambda item: item["score"]["overall"], reverse=True)
```

- [ ] **Step 4: Run tests**

Run:

```powershell
cd prototype
python -m pytest tests\test_recommendation.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add prototype docs/agent_handoff.md
git commit -m "feat: recommend moisturizing formula candidates"
```

---

### Task 6: Implement Feedback Learning

**Files:**
- Create: `prototype/rjm_formula_ai/feedback.py`
- Create: `prototype/tests/test_feedback_learning.py`
- Modify: `docs/agent_handoff.md`

**Interfaces:**
- Consumes:
  - `IngredientRelation`
  - experiment feedback JSON
- Produces:
  - `apply_feedback_to_relations(relations, feedback_rows) -> list[IngredientRelation]`

- [ ] **Step 1: Write failing feedback test**

Create `prototype/tests/test_feedback_learning.py`:

```python
from pathlib import Path

from rjm_formula_ai.feedback import apply_feedback_to_relations
from rjm_formula_ai.load_data import load_relations


ROOT = Path(__file__).resolve().parents[2]


def test_successful_feedback_increases_relation_weight():
    relations = load_relations(ROOT / "data" / "samples" / "ingredient_relations.moisturizing.json")
    updated = apply_feedback_to_relations(
        relations,
        [{"result": "pass", "ingredient_ids": ["ING-GLYCERIN", "ING-SODIUM-HYALURONATE"]}],
    )
    before = relations[0].feedback_weight
    after = updated[0].feedback_weight
    assert after > before
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
cd prototype
python -m pytest tests\test_feedback_learning.py -v
```

Expected: FAIL because `feedback.py` does not exist.

- [ ] **Step 3: Implement feedback logic**

Create `prototype/rjm_formula_ai/feedback.py`:

```python
from dataclasses import replace

from .models import IngredientRelation


def apply_feedback_to_relations(
    relations: list[IngredientRelation],
    feedback_rows: list[dict],
) -> list[IngredientRelation]:
    updated = relations
    for feedback in feedback_rows:
        ingredient_ids = set(feedback.get("ingredient_ids", []))
        delta = 0.05 if feedback.get("result") == "pass" else -0.05
        next_rows: list[IngredientRelation] = []
        for relation in updated:
            applies = (
                relation.source_ingredient_id in ingredient_ids
                and relation.target_ingredient_id in ingredient_ids
            )
            if applies:
                next_rows.append(
                    replace(
                        relation,
                        feedback_weight=max(-0.3, min(0.3, relation.feedback_weight + delta)),
                    )
                )
            else:
                next_rows.append(relation)
        updated = next_rows
    return updated
```

- [ ] **Step 4: Run tests**

Run:

```powershell
cd prototype
python -m pytest tests\test_feedback_learning.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add prototype docs/agent_handoff.md
git commit -m "feat: update ingredient relations from experiment feedback"
```

---

### Task 7: Create End-to-End CLI Demo

**Files:**
- Create: `prototype/rjm_formula_ai/cli.py`
- Create: `scripts/run_formula_demo.ps1`
- Modify: `prototype/README.md`
- Modify: `docs/agent_handoff.md`

**Interfaces:**
- Consumes:
  - `recommend_formulas`
  - sample data
- Produces:
  - `data/outputs/formula_recommendations.before_feedback.json`
  - `data/outputs/formula_recommendations.after_feedback.json`

- [ ] **Step 1: Implement CLI**

Create `prototype/rjm_formula_ai/cli.py`:

```python
import json
from pathlib import Path

from .feedback import apply_feedback_to_relations
from .load_data import load_formula_requests, load_ingredients, load_relations
from .recommend import recommend_formulas


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    project_root = root.parent
    ingredients = load_ingredients(project_root / "data" / "samples" / "ingredients.moisturizing.json")
    relations = load_relations(project_root / "data" / "samples" / "ingredient_relations.moisturizing.json")
    request = load_formula_requests(project_root / "data" / "samples" / "formula_requests.json")[0]

    before = recommend_formulas(request, ingredients, relations, limit=3)
    output_dir = project_root / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "formula_recommendations.before_feedback.json").write_text(
        json.dumps(before, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    feedback_rows = [
        {
            "result": "pass",
            "ingredient_ids": [
                item["ingredient_id"]
                for item in before[0]["ingredients"]
            ],
        }
    ]
    updated_relations = apply_feedback_to_relations(relations, feedback_rows)
    after = recommend_formulas(request, ingredients, updated_relations, limit=3)
    (output_dir / "formula_recommendations.after_feedback.json").write_text(
        json.dumps(after, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Generated formula recommendation demo outputs.")
    print(output_dir / "formula_recommendations.before_feedback.json")
    print(output_dir / "formula_recommendations.after_feedback.json")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create PowerShell script**

Create `scripts/run_formula_demo.ps1`:

```powershell
$ErrorActionPreference = "Stop"
Push-Location "$PSScriptRoot\..\prototype"
python -m rjm_formula_ai.cli
Pop-Location
```

- [ ] **Step 3: Update README**

Create `prototype/README.md`:

```markdown
# RJM Formula AI Prototype

## Run tests

```powershell
cd prototype
python -m pytest tests -v
```

## Run moisturizing formula demo

```powershell
.\scripts\run_formula_demo.ps1
```

## Expected outputs

- `data/outputs/formula_recommendations.before_feedback.json`
- `data/outputs/formula_recommendations.after_feedback.json`
```

- [ ] **Step 4: Run full test and demo**

Run:

```powershell
cd prototype
python -m pytest tests -v
cd ..
.\scripts\run_formula_demo.ps1
```

Expected:

- all tests PASS.
- both output JSON files are created.

- [ ] **Step 5: Commit**

Run:

```bash
git add prototype scripts data/outputs docs/agent_handoff.md
git commit -m "feat: add end-to-end formula recommendation demo"
```

---

### Task 8: Prepare Yuxi Knowledge Base Integration Notes

**Files:**
- Create: `docs/yuxi_integration.md`
- Modify: `docs/agent_handoff.md`

**Interfaces:**
- Consumes: Yuxi knowledge base already built in `F:\zky\Yuxi-main`.
- Produces: clear integration instructions for later Yuxi-specific Agent.

- [ ] **Step 1: Create integration document**

Create `docs/yuxi_integration.md`:

```markdown
# Yuxi Integration Notes

## Purpose

Use Yuxi as the knowledge and graph base for RJM formula AI.

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

- query knowledge base by功效目标, 原料名称, INCI, 风险标签.
- open source document chunk for evidence.
- retrieve ingredient relation evidence.
- write extracted structured facts to RJM prototype JSON first, then database later.

## Do Not

- Do not overwrite existing Yuxi knowledge base data.
- Do not change Yuxi deployment configuration without a separate task.
- Do not expose private MinIO files publicly.
```

- [ ] **Step 2: Update handoff**

Append:

```markdown

## Task 8 Notes

- Yuxi integration notes created.
- Later Yuxi work must begin by reading `docs/yuxi_integration.md`.
```

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/yuxi_integration.md docs/agent_handoff.md
git commit -m "docs: add yuxi integration notes for formula ai"
```

---

## 6. Execution Order

Run tasks in this order:

1. Task 1: project skeleton.
2. Task 2: JSON Schemas.
3. Task 3: moisturizing sample data.
4. Task 4: Python models and loader.
5. Task 5: recommendation prototype.
6. Task 6: feedback learning.
7. Task 7: end-to-end CLI demo.
8. Task 8: Yuxi integration notes.

After Task 8, the project has a working local prototype that later agents can extend toward:

- Yuxi知识库检索接入。
- Neo4j图谱读写。
- FastAPI服务化。
- Java管理系统一期。
- 真实供应商采购流程。

---

## 7. Self-Review

### Spec coverage

- 原料图谱：covered by Ingredient and IngredientRelation schemas plus Yuxi integration notes.
- 保湿配方推荐：covered by Tasks 3, 5, and 7.
- 工程师筛选：covered by FormulaScreening schema and Task 2.
- 实验反馈：covered by ExperimentFeedback schema and Task 6.
- AI进化：covered by feedback weight update in Task 6.
- 原料供应商采购：covered by RawMaterialSku schema and Procurement Agent.
- 一人公司执行：covered by task size, completion definition, and handoff rules.

### Placeholder scan

No unresolved placeholder markers or unspecified implementation steps remain. Later tasks are intentionally scoped as future extensions only after the MVP prototype.

### Type consistency

The function names used by later tasks match earlier definitions:

- `load_ingredients`
- `load_relations`
- `load_formula_requests`
- `recommend_formulas`
- `apply_feedback_to_relations`

---

## 8. Agent Handoff Prompt

后续Agent可以直接使用以下提示继续：

```text
请读取 F:\zky\RJM\docs\superpowers\plans\2026-07-27-rjm-formula-ai-development-plan.md，并从第一个未完成任务开始执行。每完成一个任务，运行对应验证命令，更新 F:\zky\RJM\docs\agent_handoff.md，然后停止等待复核。
```
