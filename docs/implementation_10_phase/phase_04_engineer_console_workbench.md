# Phase 04 工程师工作台增强

## 目标

让配方工程师可以在一个页面完成：输入需求、查看推荐 list、查看证据、筛选配方、提交实验反馈、查看反馈影响。

## 范围

- 静态控制台继续保持无构建依赖。
- 优先改交互效率，不做复杂 UI 框架迁移。
- 所有关键按钮都有明确状态：加载中、成功、失败。

## 建议文件

- 修改：`ui/engineer-console/index.html`
- 修改：`ui/engineer-console/app.js`
- 修改：`ui/engineer-console/styles.css`
- 修改测试：`prototype/tests/test_engineer_console_ui.py`

## 工作台布局

- 左侧：需求输入与知识状态。
- 中间：推荐配方列表、分数、原料、证据。
- 右侧：筛选记录、实验反馈、学习解释、采购建议。

## 验收命令

```powershell
cd F:\zky\RJM
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py
node --check ui\engineer-console\app.js
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=ManagementConsoleWebTests,ManagementApiMockMvcTests" test
```

## 退出标准

- 不启动服务也能看到离线样例。
- Java 服务启动后能走真实 API。
- 页面文案无乱码。
## Phase 04 Completion Notes

- Added an `operationStatus` area so every key console action can show loading, success, and failure status.
- Added a `selectedFormulaSummary` area so engineers can see the currently selected formula, score, ingredient count, and first ingredient IDs before screening, feedback, explanation, or procurement.
- Wrapped key buttons with `withActionStatus`, preserving the static no-build console while giving each action a clear transient state.
- Added CSS for stable status and summary panels so the right-side workflow remains readable on desktop and mobile.
- Java console hosting tests now assert that the served console shell includes the workbench status and selected formula summary structure.

## Phase 04 Verification

```powershell
cd F:\zky\RJM
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py
node --check ui\engineer-console\app.js
cd F:\zky\RJM\java-management\management-service
mvn "-Dtest=ManagementConsoleWebTests,ManagementApiMockMvcTests" test
```
