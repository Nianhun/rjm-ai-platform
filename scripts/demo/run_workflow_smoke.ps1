$ErrorActionPreference = "Stop"
Push-Location "$PSScriptRoot\..\.."
$env:PYTHONPATH = "$PWD\apps\ai-engine-python\src"
& "C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m rjm_formula_ai.workflow_smoke @args
Pop-Location
