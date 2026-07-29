$ErrorActionPreference = "Stop"
# Compatibility wrapper around run_prototype_stack.ps1.
& (Join-Path $PSScriptRoot "development\run_local_demo.ps1") @args
