# Phase 02 DB 生产化最小配置

## 目标

让 Java 管理系统的 `db` 模式不只存在于测试里，而是可以通过本地配置启动，用 H2 文件库或 SQLite 作为一人公司早期持久化数据库。

## 范围

- 新增本地 DB profile 或配置示例。
- 给 `db` 模式提供明确 DataSource。
- 启动时自动初始化 schema。
- 不引入复杂迁移体系，Flyway/Liquibase 放到后续。

## 建议文件

- 修改：`java-management/management-service/src/main/resources/application.yml`
- 新增：`java-management/management-service/src/main/resources/application-db-local.yml`
- 新增或修改：`scripts/run_java_db_local.ps1`
- 修改：`java-management/management-service/README.md`

## 开发任务

1. 写 Spring Boot 配置测试，证明 `rjm.ai-service.mode=db` 且本地 profile 可创建 DataSource。
2. 加 H2 文件库配置，例如 `jdbc:h2:file:F:/zky/RJM/data/runtime/java-db/rjm_formula_ai`。
3. 增加启动脚本，设置 profile 并启动 Java 服务。
4. 文档写明如何清理本地库、如何切回 `mock` 或 `python`。

## 验收命令

```powershell
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=DbModeManagementApiTests,DbModeH2IntegrationTests" test
cd F:\zky\RJM
.\scripts\run_java_db_local.ps1 -SmokeOnly
```

## 退出标准

- 本地 DB 模式能启动。
- 推荐接口能写入真实本地库。
- 重启后归档配方仍可查询。

## 当前实现记录

- 已新增 `DbLocalDataSourceConfig`，在 `rjm.local-db.enabled=true` 时创建 H2 `JdbcDataSource`。
- 已新增 `application-db-local.yml`，默认文件库路径为 `data/runtime/java-db/rjm_formula_ai`。
- 已新增 `scripts/run_java_db_local.ps1`，支持 `-SmokeOnly` 验证和普通启动。
