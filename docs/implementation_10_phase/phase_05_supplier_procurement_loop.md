# Phase 05 供应商与采购闭环

## 目标

把“AI 推荐配方后找到原材料供应商采购”的流程补成可记录、可追踪、可筛选的业务闭环。

## 范围

- 原料 SKU 数据可导入。
- 采购推荐结果可落库。
- 工程师或采购人员可标记采购状态。

## 建议文件

- 修改 schema：`raw_material_sku`、`procurement_recommendation`
- 新增 Repository：`RawMaterialSkuRepository`、`ProcurementRecommendationRepository`
- 修改 Controller：`ProcurementController`
- 修改 UI：采购建议面板

## 状态枚举

- `matched`: 找到候选供应商。
- `sample_requested`: 已申请样品。
- `sample_received`: 已收到样品。
- `approved`: 供应商可用于该配方。
- `rejected`: 不采用。
- `missing_supplier`: 暂无供应商。

## 验收命令

```powershell
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=ProcurementRepositoryTests,ManagementApiMockMvcTests,DbModeH2IntegrationTests" test
```

## 退出标准

- 输入 formula_id 能生成采购建议。
- 建议能保存和查询。
- 缺供应商原料会被明确列出。
## Phase 05 Completion Notes

- Added `ProcurementRecommendationRepository` to persist procurement recommendation rows and raw material SKU snapshots in DB mode.
- `POST /api/procurement/recommend` now saves generated procurement suggestions when Java runs with `rjm.ai-service.mode=db`.
- Added `GET /api/procurement/recommendations/{formulaId}` to query saved procurement recommendations for a formula.
- Added `PATCH /api/procurement/recommendations/{formulaId}/{ingredientId}/status` to move procurement status through `sample_requested`, `sample_received`, `approved`, `rejected`, and related states.
- Engineer console now has `已存采购` and `申请样品` actions so a formula engineer can query persisted procurement rows and request samples from the current formula's first ingredient.
- OpenAPI documents procurement query and status update endpoints.

## Phase 05 Verification

```powershell
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=ProcurementRecommendationRepositoryTests,DbModeH2IntegrationTests,ManagementApiMockMvcTests" test
cd F:\zky\RJM
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py
node --check ui\engineer-console\app.js
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py
```
