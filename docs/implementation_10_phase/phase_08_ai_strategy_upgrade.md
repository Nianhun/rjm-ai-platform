# Phase 08 AI 推荐策略升级

## 目标

把 Python 推荐从单一规则函数升级为可插拔策略层，为后续接入 LLM、图谱推理、贝叶斯优化或实验设计算法留接口。

## 范围

- 保留当前规则推荐作为 `baseline` 策略。
- 增加策略接口和策略选择参数。
- 先不引入新外部依赖。

## 建议文件

- Python 新增：`prototype/rjm_formula_ai/strategy.py`
- Python 修改：`recommend.py`、`service.py`
- Java/OpenAPI：请求 constraints 中允许 `strategy`
- 测试：`prototype/tests/test_recommendation_strategy.py`

## 策略接口草案

```python
class RecommendationStrategy:
    def recommend(self, request, knowledge, feedback_events):
        ...
```

## 初版策略

- `baseline`: 当前规则。
- `learned_weight`: 显式读取反馈/权重后加权。
- `exploration`: 给低证据但低风险组合保留少量探索名额。

## 验收命令

```powershell
cd F:\zky\RJM
$env:PYTHONPATH="$PWD\prototype"
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_recommendation_strategy.py
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_service_api.py
```

## 退出标准

- 不传策略时行为不变。
- 传入策略时可稳定选择推荐算法。
- 后续接 LLM 不需要改 Java 控制器。

## 完成记录

- 新增 `prototype/rjm_formula_ai/strategy.py`，定义 `RecommendationStrategy` 抽象层和 `baseline`、`learned_weight`、`exploration` 三个初版策略。
- `FormulaAIService.recommend` 支持从 `constraints.strategy` 选择策略；未知策略回退到 `baseline`。
- `FormulaAIService.feedback_recommend` 默认使用 `learned_weight`，保持“反馈后重新推荐”的业务语义。
- Java `FormulaRecommendationResponse` 和 `FormulaCandidate` DTO 已增加 `strategy` 字段，Python mode 不会丢失策略来源。
- 工程师工作台新增推荐策略下拉框，请求会把 `constraints.strategy` 传给 Java/Python 推荐链路。
- OpenAPI 和 API 契约 README 已记录策略字段，响应体和候选配方都会返回实际使用的 `strategy`。

## 实际验证

```powershell
$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_recommendation_strategy.py
$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py
node --check ui\engineer-console\app.js
```

以上命令已通过。完整收尾验证记录见 `docs/agent_handoff.md`。
