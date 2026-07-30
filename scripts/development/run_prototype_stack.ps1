param(
    [switch]$SmokeOnly,
    [switch]$UseYuxiKnowledge,
    [string]$BindHost = "127.0.0.1",
    [string]$PythonPort = "8000",
    [string]$JavaPort = "8080",
    [switch]$UseYuxiGraphOnline,
    [string]$YuxiApiBase = "http://127.0.0.1:5050",
    [string]$YuxiKbId = "",
    [string]$YuxiApiToken = "",
    [string]$AiBaseUrl = "",
    [string]$AiApiKey = "",
    [string]$AiModel = "",
    [string]$AiChatCompletionsPath = "",
    [string]$AiHttpClient = "",
    [string]$AiTimeoutSeconds = "",
    [string]$ApiToken
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\..\.."
$runtimeDir = Join-Path $root "data\runtime\local_demo"
$pythonExe = "C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

function Repair-DuplicatePathEnvironment {
    $processEnvironment = [Environment]::GetEnvironmentVariables("Process")
    $hasUpperPath = @($processEnvironment.Keys | Where-Object { $_ -ceq "PATH" }).Count -gt 0
    if (-not $hasUpperPath) {
        return
    }

    $pathValue = [Environment]::GetEnvironmentVariable("Path", "Process")
    if (-not $pathValue) {
        $pathValue = [Environment]::GetEnvironmentVariable("PATH", "Process")
    }

    [Environment]::SetEnvironmentVariable("PATH", $null, "Process")
    if ($pathValue) {
        [Environment]::SetEnvironmentVariable("Path", $pathValue, "Process")
    }
}

function Start-SanitizedProcess {
    param(
        [string]$Command,
        [string]$WorkingDirectory,
        [string]$OutLog,
        [string]$ErrLog
    )

    $powershellExe = Join-Path $PSHOME "powershell.exe"
    $startScript = [System.IO.Path]::ChangeExtension($OutLog, ".start.ps1")
    @(
        '$ErrorActionPreference = "Stop"',
        $Command
    ) | Set-Content -Path $startScript -Encoding UTF8
    Repair-DuplicatePathEnvironment
    return Start-Process `
        -FilePath $powershellExe `
        -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $startScript) `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $OutLog `
        -RedirectStandardError $ErrLog `
        -WindowStyle Hidden `
        -PassThru
}

if ($SmokeOnly) {
    Write-Host "SmokeOnly: prototype stack configuration is parseable."
    Write-Host "Python AI health: http://${BindHost}:$PythonPort/health"
    Write-Host "Java management health: http://${BindHost}:$JavaPort/api/health"
    Write-Host "Engineer console: http://${BindHost}:$JavaPort/console/"
    Write-Host "Runtime logs: $runtimeDir"
    Write-Host "API token enabled: $([bool]$ApiToken)"
    Write-Host "Yuxi online graph: $([bool]$UseYuxiGraphOnline), API: $YuxiApiBase"
    return
}

$pythonEnv = @(
    "`$env:SSLKEYLOGFILE = `$null",
    "`$env:PYTHONPATH = '$root\apps\ai-engine-python\src'",
    "`$env:RJM_HTTP_HOST = '$BindHost'",
    "`$env:RJM_HTTP_PORT = '$PythonPort'",
    "`$env:RJM_FORMULA_PATH = '$runtimeDir\formula_candidates.jsonl'",
    "`$env:RJM_FEEDBACK_PATH = '$runtimeDir\feedback_events.jsonl'",
    "`$env:RJM_SCREENING_PATH = '$runtimeDir\screening_events.jsonl'"
)

if ($UseYuxiGraphOnline) {
    $pythonEnv += "`$env:RJM_YUXI_GRAPH_ENABLED = 'true'"
    $pythonEnv += "`$env:RJM_YUXI_API_BASE = '$YuxiApiBase'"
    if ($YuxiKbId) {
        $pythonEnv += "`$env:RJM_YUXI_KB_ID = '$YuxiKbId'"
    }
    if ($YuxiApiToken) {
        $pythonEnv += "`$env:RJM_YUXI_API_TOKEN = '$YuxiApiToken'"
    }
    if ($env:RJM_YUXI_TIMEOUT_SECONDS) {
        $pythonEnv += "`$env:RJM_YUXI_TIMEOUT_SECONDS = '$env:RJM_YUXI_TIMEOUT_SECONDS'"
    }
}

if ($UseYuxiKnowledge) {
    powershell -ExecutionPolicy Bypass -File (Join-Path $root "scripts\integration\run_yuxi_import.ps1")
    $pythonEnv += "`$env:RJM_INGREDIENTS_PATH = '$root\data\yuxi_import\ingredients.yuxi.json'"
    $pythonEnv += "`$env:RJM_RELATIONS_PATH = '$root\data\yuxi_import\ingredient_relations.yuxi.json'"
    $pythonEnv += "`$env:RJM_EVIDENCE_PATH = '$root\data\yuxi_import\evidence.yuxi.json'"
}

if ($AiBaseUrl) {
    $pythonEnv += "`$env:RJM_AI_BASE_URL = '$AiBaseUrl'"
}
if ($AiApiKey) {
    $pythonEnv += "`$env:RJM_AI_API_KEY = '$AiApiKey'"
}
if ($AiModel) {
    $pythonEnv += "`$env:RJM_AI_MODEL = '$AiModel'"
}
if ($AiChatCompletionsPath) {
    $pythonEnv += "`$env:RJM_AI_CHAT_COMPLETIONS_PATH = '$AiChatCompletionsPath'"
}
if ($AiHttpClient) {
    $pythonEnv += "`$env:RJM_AI_HTTP_CLIENT = '$AiHttpClient'"
}
if ($AiTimeoutSeconds) {
    $pythonEnv += "`$env:RJM_AI_TIMEOUT_SECONDS = '$AiTimeoutSeconds'"
}

$pythonCommand = ($pythonEnv -join "; ") + "; & '$pythonExe' -m rjm_formula_ai.http_server"

$tokenEnabled = [bool]$ApiToken
$tokenArguments = "--rjm.security.api-token.enabled=$tokenEnabled"
if ($tokenEnabled) {
    $tokenArguments = "$tokenArguments --rjm.security.api-token.value=$ApiToken"
}

$pythonOutLog = Join-Path $runtimeDir "python-ai.out.log"
$pythonErrLog = Join-Path $runtimeDir "python-ai.err.log"
$javaOutLog = Join-Path $runtimeDir "java-management.out.log"
$javaErrLog = Join-Path $runtimeDir "java-management.err.log"

$pythonProcess = Start-SanitizedProcess `
    -Command $pythonCommand `
    -WorkingDirectory $root `
    -OutLog $pythonOutLog `
    -ErrLog $pythonErrLog

$javaDir = Join-Path $root "apps\java-admin-service"
$javaRunArguments = "--server.address=$BindHost --server.port=$JavaPort --rjm.ai-service.mode=python --rjm.python-ai.base-url=http://${BindHost}:$PythonPort $tokenArguments"
$javaCommand = "mvn spring-boot:run '-Dspring-boot.run.arguments=$javaRunArguments'"
$javaProcess = Start-SanitizedProcess `
    -Command $javaCommand `
    -WorkingDirectory $javaDir `
    -OutLog $javaOutLog `
    -ErrLog $javaErrLog

Write-Host "Python AI PID: $($pythonProcess.Id), health: http://${BindHost}:$PythonPort/health"
Write-Host "Java management PID: $($javaProcess.Id), health: http://${BindHost}:$JavaPort/api/health"
Write-Host "Engineer console: http://${BindHost}:$JavaPort/console/"
Write-Host "Runtime logs: $runtimeDir"
Write-Host "Yuxi online graph: $([bool]$UseYuxiGraphOnline), API: $YuxiApiBase"
Write-Host "API token header: X-RJM-API-Token"
Write-Host "Stop services: Stop-Process -Id $($pythonProcess.Id),$($javaProcess.Id)"
