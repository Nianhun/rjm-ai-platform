$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "integration\run_java_python_integration_smoke.ps1") @args
