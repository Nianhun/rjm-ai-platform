# Phase 07 实验批次管理

## 目标

把实验反馈从单条事件升级为实验批次管理，支持配方工程师记录小试/中试指标、问题、结论和附件引用。

## 范围

- 建立实验批次表。
- 反馈事件关联批次。
- 指标结构保持 JSON，避免过早固定所有实验字段。

## 建议文件

- schema：新增 `experiment_batch`
- Java DTO：`ExperimentBatchRequest`、`ExperimentBatchResponse`
- Java Repository：`ExperimentBatchRepository`
- Java Controller：`ExperimentBatchController`
- UI：实验反馈区域增加批次选择/创建

## 核心字段

- `batch_no`
- `formula_id`
- `stage`: `lab_trial`、`pilot`、`stability`
- `owner`
- `metrics_json`
- `issues_json`
- `conclusion`
- `status`

## 验收命令

```powershell
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=ExperimentBatchRepositoryTests,ManagementApiMockMvcTests,DbModeH2IntegrationTests" test
```

## 退出标准

- 能创建批次。
- 能把反馈关联到批次。
- 学习加权仍只使用 `pass` 结论，不被未完成批次污染。

## Phase 07 Completion Notes

- Java database schema now includes `experiment_batch` in both SQLite and H2 variants.
- Java DTOs added: `ExperimentBatchRequest`, `ExperimentBatchResponse`, and `ExperimentBatchListResponse`.
- Java repository added: `ExperimentBatchRepository`, with create and list-by-formula operations.
- Java management API now exposes:
  - `POST /api/experiments/batches`
  - `GET /api/experiments/batches?formula_id=...`
- `DbArchivingFormulaAiManagementService` persists experiment batches in DB mode; mock and python modes keep them in the Java management layer.
- Existing experiment feedback still uses `batch_no`, so feedback can be associated with a created batch.
- H2 integration verifies a `running` batch does not create feedback rows or affect learned weights until `POST /api/experiments/feedback` records a `pass` result.
- Engineer console adds `创建实验批次` and `实验批次` actions.
- OpenAPI and Java API mapping docs include the experiment batch endpoints.

## Verification

```powershell
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=ExperimentBatchRepositoryTests,ManagementApiMockMvcTests,DbModeManagementApiTests,DbModeH2IntegrationTests" test
cd F:\zky\RJM
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_database_schema.py
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py
node --check ui\engineer-console\app.js
```
