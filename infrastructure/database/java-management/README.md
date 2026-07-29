# Java 管理系统数据库草案

这份 schema 是给一人公司节奏准备的持久化底座：先 SQLite/H2 验证，再由后续 Java agent 迁入 Flyway/Liquibase，最后按部署环境迁移到 MySQL 或 PostgreSQL。

## 范围

`schema.sql` 覆盖当前闭环的最小业务记录。`schema.h2.sql` 是 H2 集成测试使用的等价变体，主要差异是自增列语法从 SQLite 的 `autoincrement` 改为 H2 的 `auto_increment`。

- `formula_request`: 用户提出的功效目标、剂型和约束。
- `formula_candidate`: AI 生成的候选配方快照，保留完整 JSON、评分、证据和风险说明。
- `formula_screening`: 配方工程师的保留、拒绝或修改意见。
- `experiment_batch`: 小试、中试或稳定性实验批次，保存阶段、负责人、指标、问题、结论和状态。
- `experiment_feedback`: 小试或实验反馈，用于后续推荐学习。
- `evidence_record`: Yuxi 导入或检索得到的证据来源。
- `raw_material_sku`: 原料供应商 SKU、价格、资质和交期。
- `procurement_recommendation`: 某个候选配方触发的采购推荐结果。

## 落地顺序

1. 保持 Python 原型继续写 JSONL，Java 管理系统继续通过 HTTP 调 Python。
2. 在 Java 侧引入数据库后，先把 `formula_candidate`、`formula_screening`、`experiment_feedback` 三类运行时记录落库。
3. 再导入 `evidence_record` 和 `raw_material_sku`，让证据追溯和采购推荐也可审计。
4. 后续迁移到 MySQL 或 PostgreSQL，并把 `text` 类型中的 JSON 字段改成目标数据库的原生 JSON 类型。

## 设计原则

- 先保存完整 JSON 快照，保证推荐结果可追溯。
- 表字段只承载检索和审计需要的稳定字段，复杂结构暂存在 JSON 字段中。
- `formula_id` 不是全局唯一主键，因为同一个配方 ID 可能在不同请求或不同算法版本中再次生成；查询最近候选时按 `created_at` 或自增 `id` 倒序。
- 后续需要算法版本化时，在 `formula_candidate` 增加 `algorithm_version`、`knowledge_snapshot_id`、`model_config_json`。

## 当前 Java 入口

`management-service` 已提供第一条 JDBC 边界：

- `FormulaCandidateArchiveRepository.saveRecommendation(...)`: 将推荐响应保存为 `formula_request` 和 `formula_candidate`。
- `FormulaCandidateArchiveRepository.findLatestByFormulaId(...)`: 按 `formula_id` 读取最近候选配方快照。
- `FormulaScreeningRepository.recordScreening(...)`: 将工程师筛选意见保存为 `formula_screening`。
- `FormulaScreeningRepository.listScreening(...)`: 按 `formula_id` 查询工程师筛选意见。
- `DbArchivingFormulaAiManagementService`: `rjm.ai-service.mode=db` 时启用，推荐逻辑暂用内存实现，推荐结果通过 Repository 落库，归档查询从 Repository 读取。

该 Repository 只依赖 `javax.sql.DataSource` 和 Jackson。当前代码已经提供 `db` service mode 的 Spring 装配边界，但还没有引入数据库驱动或真实 `DataSource` 配置；后续接入 H2、SQLite、MySQL 或 PostgreSQL 后即可进行端到端数据库模式验证。
## Current Java JDBC Addendum

- `ExperimentFeedbackRepository.recordFeedback(...)`: saves lab or pilot experiment feedback into `experiment_feedback`.
- `ExperimentFeedbackRepository.countByFormulaId(...)`: counts feedback rows for one formula id.
- `DbArchivingFormulaAiManagementService` in `rjm.ai-service.mode=db` now persists candidate archives, engineer screening records, experiment batches, and experiment feedback through JDBC repositories.
- `learned_weight`: stores auditable learned weights for formula, ingredient, and ingredient-pair boosts.
- `LearnedWeightRepository.saveWeight(...)`: updates or inserts one learned weight by `goal`, `target_type`, and `target_key`, preserving the weight, evidence count, source, and calculation note.

## Phase 07 Experiment Batch Addendum

- `experiment_batch`: stores one lab trial, pilot, or stability batch by `batch_no`, `formula_id`, `stage`, `owner`, JSON metrics, JSON issues, conclusion, and status.
- `ExperimentBatchRepository.createBatch(...)`: writes a batch record without changing recommendation learning.
- `ExperimentBatchRepository.listBatchesByFormula(...)`: lists batches for a formula in newest-first order.
- Learning still uses `experiment_feedback.result = 'pass'`; planned or running batches do not change learned weights until feedback is recorded.

## Phase 06 Knowledge Governance Addendum

- `knowledge_import_batch`: stores one Yuxi import batch ledger with source files, output files, counts, imported time, and governance notes.
- `ingredient_alias`: reserves a normalized alias table for INCI, Chinese names, supplier names, and later manually reviewed aliases.
