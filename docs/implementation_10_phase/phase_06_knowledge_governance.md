# Phase 06 知识库治理

## 目标

让 Yuxi 知识导入不只是一次性脚本，而是可重复、可检查、可解释的知识库治理流程。

## 范围

- 导入批次记录。
- 原料别名和标准 ID 管理。
- 关系来源、关系类型、可信度可追踪。
- 不在本期做复杂人工标注系统。

## 建议文件

- Python：`prototype/rjm_formula_ai/yuxi_import.py`
- Python 测试：`prototype/tests/test_yuxi_import.py`
- Java schema：新增 `knowledge_import_batch`、可选 `ingredient_alias`
- 文档：`docs/yuxi_integration.md`

## 验收命令

```powershell
cd F:\zky\RJM
.\scripts\run_yuxi_import.ps1
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_yuxi_import.py
```

## 退出标准

- 每次导入能知道来源文件、导入时间、原料数、关系数、证据数。
- 重复导入结果稳定。
- 证据 ID 能回溯到 Yuxi 来源。

## Phase 06 Completion Notes

- Yuxi import now writes `data/yuxi_import/import_batch.yuxi.json` with `batch_id`, `imported_at`, source files, output files, counts, and governance notes.
- Python `FormulaAIService.knowledge_governance()` summarizes evidence source types, relation types, relation confidence buckets, alias coverage, missing evidence IDs, and governance warnings.
- Python HTTP service exposes `GET /knowledge/governance`.
- Java management API exposes `GET /api/knowledge/governance` through `KnowledgeController`, `KnowledgeGovernanceResponse`, `PythonFormulaAiClient`, and all service modes.
- Java database schema draft now includes `knowledge_import_batch` and `ingredient_alias`.
- Engineer console adds a `知识治理` action and offline governance sample.
- OpenAPI and Java/Python mapping docs now include the governance endpoint.

## Verification

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_yuxi_import.ps1
$env:PYTHONPATH = "$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_service_api.py
$env:PYTHONPATH = "$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_yuxi_import.py
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_database_schema.py
node --check ui\engineer-console\app.js
mvn "-Dtest=ManagementApiMockMvcTests,PythonFormulaAiClientTests" test
```
