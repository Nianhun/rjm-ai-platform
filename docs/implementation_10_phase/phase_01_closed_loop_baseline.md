# Phase 01 闭环基线冻结

## 目标

把当前已经实现的“推荐、筛选、实验反馈、学习加权、采购、证据追溯、DB 持久化”冻结成稳定基线，作为后续 9 期的起点。

## 当前范围

- Python 原型服务可运行。
- Java 管理服务 `mock`、`python`、`db` 三种模式可测试。
- Yuxi 导入已能生成原料、关系和证据。
- DB 模式已支持候选配方归档、工程师筛选、实验反馈、反馈影响报告、配方级/原料级/原料组合级学习加权、`learned_weight` 审计表。

## 开发任务

1. 更新 `docs/agent_handoff.md`，确保最新完成任务、验证命令和下一步准确。
2. 保持 `java-management/database/schema.sql` 与 `schema.h2.sql` 同步。
3. 保持 `prototype/tests/test_database_schema.py` 覆盖核心闭环表。
4. 跑 Java 和 Python 基线测试。

## 验收命令

```powershell
cd F:\zky\RJM
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_database_schema.py
cd F:\zky\RJM\java-management\management-service
mvn test
```

## 退出标准

- Python schema 测试通过。
- Java 全量测试通过。
- `docs/agent_handoff.md` 写明当前最新任务和下一期入口。

