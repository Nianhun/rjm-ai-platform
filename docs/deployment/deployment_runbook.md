# 瑞吉明配方 AI 初版部署 Runbook

## 默认模式

初版默认只绑定本机地址 `127.0.0.1`：

- Python AI: `http://127.0.0.1:8000`
- Java 管理系统: `http://127.0.0.1:8080`
- 工程师工作台: `http://127.0.0.1:8080/console/index.html`

启动前可参考 `.env.example`。不要把供应商价格、实验结论、配方比例和采购状态暴露到公网。

## 启动

```powershell
cd F:\zky\RJM
.\scripts\run_prototype_stack.ps1 -UseYuxiKnowledge
```

快速检查脚本和默认配置：

```powershell
.\scripts\run_prototype_stack.ps1 -SmokeOnly
```

需要内网访问时显式指定绑定地址，并先确认网络隔离和访问人群：

```powershell
.\scripts\run_prototype_stack.ps1 -BindHost 0.0.0.0 -ApiToken "replace-with-internal-secret"
```

## 访问控制

Java API 支持最小 token gate。启用后，请求 `/api/**` 必须带：

```text
X-RJM-API-Token: replace-with-internal-secret
```

本地演示可不启用 token。内网试用必须启用 token，并且只通过可信网络访问。正式版本再接公司账号体系、角色权限和操作审计。

## 数据与日志

运行时数据和日志默认写入：

```text
data/runtime/local_demo
```

主要文件：

- `formula_candidates.jsonl`: AI 推荐候选配方归档。
- `feedback_events.jsonl`: 实验反馈事件。
- `screening_events.jsonl`: 工程师筛选记录。
- `python-ai.out.log` / `python-ai.err.log`: Python AI 服务日志。
- `java-management.out.log` / `java-management.err.log`: Java 管理系统日志。

## 停止

启动脚本会打印进程 ID。按提示停止：

```powershell
Stop-Process -Id <pythonPid>,<javaPid>
```

## 排查

先检查健康接口：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8080/api/health
```

再看日志：

```powershell
Get-Content data\runtime\local_demo\python-ai.err.log -Tail 80
Get-Content data\runtime\local_demo\java-management.err.log -Tail 80
```

常见问题：

- 端口被占用：换 `-PythonPort` 或 `-JavaPort`。
- 推荐无 Yuxi 证据：使用 `-UseYuxiKnowledge` 并检查 `data/yuxi_import` 文件是否存在。
- API 返回 401：确认 `X-RJM-API-Token` 与启动脚本的 `-ApiToken` 一致。
- Java 调不到 Python：检查 `rjm.python-ai.base-url` 是否指向 Python AI 的实际地址。

## Yuxi Online Graph Mode

The imported snapshot mode (`-UseYuxiKnowledge`) uses `data/yuxi_import/*.json`; in the current demo that is the smaller 46 ingredient / 316 relation subset. To use the full yuxi-know graph shown in the Yuxi index panel, start yuxi-know first and then start RJM with online graph mode:

```powershell
cd F:\zky\RJM
.\scripts\run_prototype_stack.ps1 -UseYuxiKnowledge -UseYuxiGraphOnline -YuxiApiBase http://127.0.0.1:5050 -JavaPort 8090 -PythonPort 8010
```

If yuxi-know requires a fixed knowledge-base ID or token, pass them explicitly:

```powershell
.\scripts\run_prototype_stack.ps1 -UseYuxiKnowledge -UseYuxiGraphOnline -YuxiApiBase http://127.0.0.1:5050 -YuxiKbId "<kb-id>" -YuxiApiToken "<token>" -JavaPort 8090 -PythonPort 8010
```

Expected status in the engineer console:

- `Yuxi graph online`: RJM can reach yuxi-know and is displaying full graph counts such as 41896 entities / 409315 relationships.
- `Yuxi offline: snapshot fallback`: RJM could not reach yuxi-know, or graph recall returned no usable formula ingredients, so it continues with the local snapshot.
- `Java API connected`: online graph mode is disabled and RJM is using only the configured local knowledge files.
