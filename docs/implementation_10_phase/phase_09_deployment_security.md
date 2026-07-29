# Phase 09 部署与安全

## 目标

让初版可以在本地或公司内网稳定启动，并具备最小安全边界。

## 范围

- 本地一键启动脚本。
- 环境变量模板。
- 基础访问控制设计。
- 日志和故障排查说明。

## 交付文件

- 新增：`.env.example`
- 修改：`scripts/run_local_demo.ps1`
- 新增：`scripts/run_prototype_stack.ps1`
- 新增：`docs/deployment_runbook.md`
- Java：可选 `X-RJM-API-Token` token gate

## 安全底线

- 不把供应商价格、实验结论、配方比例、采购状态公开到公网。
- 本地 demo 默认绑定 `127.0.0.1`。
- 如需内网访问，必须显式配置 host，并建议启用 `-ApiToken`。
- 正式版本再接入公司账号体系、角色权限和完整操作审计。

## 验收命令

```powershell
cd F:\zky\RJM
.\scripts\run_local_demo.ps1 -SmokeOnly
```

## 退出标准

- 一条命令能启动 Python + Java + 控制台。
- 文档能说明端口、数据目录、如何停止、如何排错。
- 内网访问有最小 token gate，且默认不会把 API 暴露到公网。

## 完成记录

- 新增 `.env.example`，记录本机绑定、端口、运行时数据路径、Yuxi 知识路径和 API token gate 默认值。
- 新增 `scripts/run_prototype_stack.ps1`，作为初版 Python AI + Java 管理系统 + 工程师控制台的一键启动入口。
- `scripts/run_local_demo.ps1` 保持兼容，转发到 `run_prototype_stack.ps1`，支持 `-SmokeOnly`、`-UseYuxiKnowledge` 和 `-ApiToken`。
- Java 管理系统新增可选 `X-RJM-API-Token` gate；默认关闭，启用后保护 `/api/**`，控制台静态页面仍可加载。
- CORS 方法补齐 `PATCH`，覆盖采购状态更新类 API。
- 新增 `docs/deployment_runbook.md`，说明端口、数据目录、日志、停止方式、排错步骤和安全底线。
- OpenAPI 和 API 契约 README 记录 `ApiTokenAuth` 和 `X-RJM-API-Token`。

## 实际验证

```powershell
$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_deployment_security.py
$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_local_demo_script.py
$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py
powershell -ExecutionPolicy Bypass -File .\scripts\run_prototype_stack.ps1 -SmokeOnly
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1 -SmokeOnly
cd java-management\management-service
mvn test
```
