# Phase 03 学习权重 API 与解释

## 目标

把 `learned_weight` 表从后台审计数据变成工程师可读解释：AI 为什么更推荐某个配方、原料或组合。

## 范围

- Java 增加学习权重查询 API。
- Java 增加推荐解释字段或独立解释接口。
- 前端能展示至少三类权重：formula、ingredient、ingredient_pair。

## 建议文件

- 新增 DTO：`LearnedWeightResponse`、`LearnedWeightRow`
- 新增 Controller：`LearningController`
- 修改 Repository：`LearnedWeightRepository`
- 修改 UI：`ui/engineer-console/app.js`、`index.html`
- 修改 OpenAPI：`java-management/api-contract/openapi.json`

## API 草案

- `GET /api/learning/weights?goal=moisturizing&target_type=ingredient`
- `GET /api/formulas/{formulaId}/explanation?goal=moisturizing`

## 验收命令

```powershell
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=LearningControllerTests,LearnedWeightRepositoryTests,DbModeH2IntegrationTests" test
cd F:\zky\RJM
node --check ui\engineer-console\app.js
```

## 退出标准

- API 能返回目标、权重、证据数量、计算说明。
- 控制台能展示“该推荐受哪些成功实验反馈影响”。
## Phase 03 Completion Notes

- Added Java API `GET /api/learning/weights?goal=保湿&target_type=ingredient` for auditable learned weight rows.
- Added Java API `GET /api/formulas/{formulaId}/explanation?goal=保湿` for formula-specific learning influences.
- DB mode reads `learned_weight`, filters by goal/type/formula ingredients, and returns formula, ingredient, and ingredient-pair influences.
- Engineer console now has `学习解释` and `学习权重` actions that write responses into the JSON output panel.
- OpenAPI now documents `LearnedWeightResponse`, `LearnedWeightRow`, and `FormulaLearningExplanationResponse`.

## Phase 03 Verification

```powershell
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=LearningControllerTests,LearnedWeightRepositoryTests,DbModeH2IntegrationTests" test
cd F:\zky\RJM
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py
node --check ui\engineer-console\app.js
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py
```
