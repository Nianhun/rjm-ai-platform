$ErrorActionPreference = "Stop"
# Compatibility wrapper. The implementation moved to scripts/demo/run_release_demo.ps1.
# Keeps legacy checks for release_demo_summary.json and rjm_formula_ai.release_demo valid.
& (Join-Path $PSScriptRoot "demo\run_release_demo.ps1") @args
