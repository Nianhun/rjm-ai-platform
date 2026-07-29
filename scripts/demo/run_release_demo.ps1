$ErrorActionPreference = "Stop"
Push-Location "$PSScriptRoot\..\.."

$env:PYTHONPATH = "$PWD\apps\ai-engine-python\src"
$pythonExe = "C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$output = Join-Path $PWD "data\outputs\release_demo_summary.json"
& $pythonExe -m rjm_formula_ai.release_demo --output $output @args

Write-Host "Release demo summary: $output"
Pop-Location
