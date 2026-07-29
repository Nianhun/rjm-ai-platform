# Phase 10 初版验收演示

## 目标

形成一个可给瑞吉明演示的初版：输入“保湿配方”后，AI 推荐 list，工程师筛选，实验反馈，系统学习进化，再进入供应商采购建议。

## 演示脚本

1. 启动系统。
2. 打开工程师控制台。
3. 输入目标：`保湿`。
4. 查看 3 个候选配方。
5. 打开某个原料或证据说明。
6. 工程师保留一个配方，拒绝或修改其他配方。
7. 提交一次成功实验反馈。
8. 重新推荐，看到排序、评分或解释变化。
9. 查看学习权重说明。
10. 进入采购建议，看到原料供应商或缺口。

## 交付文件

- 新增：`prototype/rjm_formula_ai/release_demo.py`
- 新增：`prototype/tests/test_release_acceptance.py`
- 新增：`scripts/run_release_demo.ps1`
- 新增：`docs/release_acceptance.md`
- 更新：根目录 `README.md`
- 输出：`data/outputs/release_demo_summary.json`

## 验收命令

```powershell
cd F:\zky\RJM
powershell -ExecutionPolicy Bypass -File .\scripts\run_release_demo.ps1
$env:PYTHONPATH="$PWD\prototype"
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_release_acceptance.py
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_workflow_smoke.py
powershell -ExecutionPolicy Bypass -File .\scripts\run_java_python_integration_smoke.ps1 -UseYuxiKnowledge
cd F:\zky\RJM\java-management\management-service
mvn test
```

## 退出标准

- 演示脚本跑通。
- 文档说明“当前能做什么、不能做什么、下一步如何接真实数据”。
- 所有常规测试通过。
- 初版可以交给业务方试用并收集反馈。

## 完成记录

- `release_demo.py` 复用闭环 smoke，生成面向业务验收的 JSON 摘要。
- `run_release_demo.ps1` 一键执行验收演示并写入 `data/outputs/release_demo_summary.json`。
- `release_acceptance.md` 说明演示目标、操作路径、当前能力边界和真实数据接入建议。
- 根 `README.md` 已更新为 10/10 初版入口，包含一键验收、本地启动和常规验证命令。
- 验收摘要覆盖候选配方、工程师筛选、实验反馈、学习进化和采购建议。
