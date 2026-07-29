$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pythonExe = "C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path -LiteralPath $pythonExe)) {
    $pythonExe = "python"
}

$env:PYTHONPATH = Join-Path $projectRoot "apps\ai-engine-python\src"

& $pythonExe -m rjm_formula_ai.yuxi_import `
    --yuxi-output "F:\zky\Yuxi-main\output" `
    --out-dir (Join-Path $projectRoot "data\yuxi_import") `
    @args
