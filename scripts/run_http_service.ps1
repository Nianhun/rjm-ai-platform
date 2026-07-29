$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "development\run_http_service.ps1") @args
