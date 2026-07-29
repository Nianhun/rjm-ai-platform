$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "database\run_java_db_local.ps1") @args
