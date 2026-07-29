# Java 管理系统 API 契约

本目录定义 Java 管理系统与 Python 配方 AI 原型之间的接口边界。当前提供 OpenAPI 契约，后续 Java 项目可以据此维护 Controller、DTO、客户端和集成测试。

## 文件

- `openapi.json`: OpenAPI 3.1 契约，覆盖推荐、候选配方归档回查、工程师筛选、实验反馈、学习权重审计、配方学习解释、采购推荐、反馈影响报告、知识源状态和证据追溯。

## Python 原型映射

| Java API | Python 原型入口 | 说明 |
| --- | --- | --- |
| `POST /api/formulas/recommend` | `FormulaAIService.recommend` | 根据功效目标和约束输出配方推荐列表。 |
| `GET /api/formulas/{formulaId}` | `FormulaAIService.get_archived_formula` | 按配方 ID 回查最近一次归档的候选配方快照，供筛选、实验和采购链路复用。 |
| `POST /api/formulas/{formulaId}/screenings` | `FormulaAIService.record_screening` | 记录配方工程师的保留、拒绝或修改意见。 |
| `GET /api/formulas/{formulaId}/screenings` | `FormulaAIService.list_screening` | 查询某个配方的工程师筛选记录。 |
| `POST /api/experiments/feedback` | `FormulaAIService.record_feedback` | 记录小试或实验反馈，供后续推荐学习使用。 |
| `POST /api/experiments/batches` | `FormulaAIService.create_experiment_batch` | 创建小试、中试或稳定性实验批次，保存阶段、负责人、指标、问题和结论。 |
| `GET /api/experiments/batches` | `FormulaAIService.list_experiment_batches` | 按配方 ID 查询实验批次，供反馈录入和工程师复盘使用。 |
| `POST /api/procurement/recommend` | `FormulaAIService.recommend_procurement` | 根据配方原料匹配供应商 SKU 和采购建议。 |
| `GET /api/procurement/recommendations/{formulaId}` | `FormulaAIService.list_procurement_recommendations` | 查询已保存的采购建议和当前采购状态。 |
| `PATCH /api/procurement/recommendations/{formulaId}/{ingredientId}/status` | `FormulaAIService.update_procurement_status` | 标记样品申请、样品收到、供应商批准或拒绝等采购状态。 |
| `POST /api/reports/feedback-impact` | `build_feedback_impact_report` | 对比反馈前后的配方排名和分数变化。 |
| `GET /api/learning/weights` | `FormulaAIService.list_learned_weights` | 查询目标功效下由通过实验反馈沉淀的公式、原料和原料组合权重。 |
| `GET /api/formulas/{formulaId}/explanation` | `FormulaAIService.explain_formula_learning` | 解释某个归档配方受到哪些学习权重影响，供配方工程师审计推荐结果。 |
| `GET /api/knowledge/status` | `FormulaAIService.knowledge_status` | 返回当前加载的原料、关系、SKU、证据目录、知识文件路径和证据来源统计。 |
| `GET /api/knowledge/governance` | `FormulaAIService.knowledge_governance` | 返回证据类型、关系类型、关系置信度、别名覆盖、缺失证据和治理提示，供知识库导入审计。 |
| `GET /api/evidence/{evidenceId}` | `FormulaAIService.get_evidence` | 按证据 ID 返回来源类型、标题、摘要、URL 和扩展元数据。 |

## 推荐策略

`POST /api/formulas/recommend` 可通过 `constraints.strategy` 选择 Python 推荐策略：

- `baseline`: 当前规则推荐路径，保留历史反馈加权后的默认行为。
- `learned_weight`: 显式读取实验反馈事件并重新加权关系图谱。
- `exploration`: 在低风险、低证据组合上保留少量探索名额。

未知策略会回退到 `baseline`。响应体和每个候选配方都会返回实际使用的 `strategy`，方便工程师台展示和后续归档审计。

## 访问控制

Java 管理 API 支持可选的本地/内网 token gate。启用 `rjm.security.api-token.enabled=true` 后，调用 `/api/**` 需要带 `X-RJM-API-Token` 请求头；本地 demo 默认关闭，内网试用建议开启。该机制是初版最小边界，正式版本仍应接入公司账号体系、角色权限和审计日志。

## Java 开发建议

1. 按 `openapi.json` 维护 DTO、Controller 和客户端测试。
2. Controller 默认可使用 mock 服务；需要真实 AI 时切换到 Python HTTP 服务。
3. 持久化侧建议优先建表：`formula_request`、`formula_candidate`、`formula_screening`、`experiment_batch`、`experiment_feedback`、`evidence_record`、`raw_material_sku`、`procurement_recommendation`。
4. 前端页面先围绕闭环最小流程开发：提交需求、查看推荐、追溯证据、工程师筛选、录入实验反馈、查看反馈影响、查看学习权重和配方解释、发起采购建议、回查采购建议、更新采购状态、查看知识源状态。

## 验证

Python 侧闭环可先运行：

```powershell
cd F:\zky\RJM
$env:PYTHONPATH = "$PWD\prototype"
python -m rjm_formula_ai.workflow_smoke
```

Java 管理系统联调可运行：

```powershell
cd F:\zky\RJM
.\scripts\run_java_python_integration_smoke.ps1 -UseYuxiKnowledge
```

## Yuxi Online Graph Mode

When Python starts with `RJM_YUXI_GRAPH_ENABLED=true`, recommendation first tries the live yuxi-know graph API. `GET /api/knowledge/status` and `POST /api/formulas/recommend` then return `knowledge_source=yuxi_graph_online` and a `yuxi_graph` object with graph counts such as `entity_count`, `relationship_count`, `total_chunks`, `indexed_chunks`, and `pending_chunks`.

If yuxi-know is offline or the graph subgraph recall returns no usable ingredient candidates, Python returns `knowledge_source=snapshot_fallback` and continues with the imported local Yuxi snapshot. In the current RJM demo this snapshot is the smaller 46 ingredient / 316 relation subset, while the live yuxi-know index can expose the full 41896 entity / 409315 relationship graph.
