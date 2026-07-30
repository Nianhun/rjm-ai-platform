param(
    [string]$BindHost = "127.0.0.1",
    [string]$PythonPort = "8000",
    [string]$JavaPort = "8080",
    [switch]$NoStopExisting,
    [switch]$SmokeOnly
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\.."
$envFile = Join-Path $root ".env.local"
$exampleFile = Join-Path $root ".env.local.example"

function Read-LocalEnvFile {
    param([string]$Path)

    $values = @{}
    if (-not (Test-Path $Path)) {
        return $values
    }

    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        $separator = $trimmed.IndexOf("=")
        if ($separator -lt 1) {
            continue
        }

        $key = $trimmed.Substring(0, $separator).Trim()
        $value = $trimmed.Substring($separator + 1).Trim().Trim('"').Trim("'")
        $values[$key] = $value
    }
    return $values
}

function Stop-PortListeners {
    param([string[]]$Ports)

    foreach ($port in $Ports) {
        $lines = netstat -ano | Select-String -Pattern "127\.0\.0\.1:$port\s+.*LISTENING\s+(\d+)"
        $pids = @()
        foreach ($line in $lines) {
            if ($line.Matches.Count -gt 0) {
                $pids += [int]$line.Matches[0].Groups[1].Value
            }
        }

        foreach ($processId in ($pids | Sort-Object -Unique)) {
            Write-Host "Stopping existing listener on port $port, PID $processId"
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    }
}

function Request-YuxiAccessToken {
    param(
        [string]$ApiBase,
        [string]$Username,
        [string]$Password
    )

    if (-not $Username -or -not $Password) {
        return ""
    }

    try {
        $body = @{
            username = $Username
            password = $Password
        }
        $response = Invoke-RestMethod `
            -Method Post `
            -ContentType "application/x-www-form-urlencoded" `
            -Body $body `
            -Uri "$ApiBase/api/auth/token"
        return [string]$response.access_token
    } catch {
        Write-Warning "Could not get Yuxi access token automatically: $($_.Exception.Message)"
        return ""
    }
}

if (-not (Test-Path $envFile)) {
    Copy-Item $exampleFile $envFile
    Write-Host "Created $envFile from .env.local.example."
    Write-Host "Default local Yuxi login settings were written. Edit .env.local if your Yuxi account differs."
}

$localEnv = Read-LocalEnvFile $envFile

$yuxiEnabled = $localEnv["RJM_YUXI_GRAPH_ENABLED"]
if (-not $yuxiEnabled) {
    $yuxiEnabled = "true"
}

$yuxiApiBase = $localEnv["RJM_YUXI_API_BASE"]
if (-not $yuxiApiBase) {
    $yuxiApiBase = "http://127.0.0.1:5050"
}

$yuxiKbId = $localEnv["RJM_YUXI_KB_ID"]
if (-not $yuxiKbId) {
    $yuxiKbId = "kb_xt1ktg3ger"
}

$yuxiApiToken = $localEnv["RJM_YUXI_API_TOKEN"]
$yuxiTimeoutSeconds = $localEnv["RJM_YUXI_TIMEOUT_SECONDS"]
if (-not $yuxiTimeoutSeconds) {
    $yuxiTimeoutSeconds = "20"
}
$aiBaseUrl = $localEnv["RJM_AI_BASE_URL"]
$aiApiKey = $localEnv["RJM_AI_API_KEY"]
$aiModel = $localEnv["RJM_AI_MODEL"]
$aiChatCompletionsPath = $localEnv["RJM_AI_CHAT_COMPLETIONS_PATH"]
$aiHttpClient = $localEnv["RJM_AI_HTTP_CLIENT"]
$aiTimeoutSeconds = $localEnv["RJM_AI_TIMEOUT_SECONDS"]
if (-not $aiTimeoutSeconds) {
    $aiTimeoutSeconds = "120"
}
$yuxiUsername = $localEnv["YUXI_ADMIN_USERNAME"]
if (-not $yuxiUsername) {
    $yuxiUsername = $localEnv["ADMIN_USERNAME"]
}
$yuxiPassword = $localEnv["YUXI_ADMIN_PASSWORD"]
if (-not $yuxiPassword) {
    $yuxiPassword = $localEnv["ADMIN_PASSWORD"]
}

if (-not $yuxiApiToken -and $yuxiEnabled.ToLowerInvariant() -in @("1", "true", "yes", "on")) {
    $yuxiApiToken = Request-YuxiAccessToken -ApiBase $yuxiApiBase -Username $yuxiUsername -Password $yuxiPassword
}

if (-not $NoStopExisting -and -not $SmokeOnly) {
    Stop-PortListeners -Ports @($PythonPort, $JavaPort)
}

$stackScript = Join-Path $root "scripts\run_prototype_stack.ps1"
$arguments = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $stackScript,
    "-UseYuxiKnowledge",
    "-BindHost", $BindHost,
    "-PythonPort", $PythonPort,
    "-JavaPort", $JavaPort
)

if ($SmokeOnly) {
    $arguments += "-SmokeOnly"
}

if ($yuxiEnabled.ToLowerInvariant() -in @("1", "true", "yes", "on")) {
    $arguments += "-UseYuxiGraphOnline"
    $arguments += "-YuxiApiBase"
    $arguments += $yuxiApiBase
    $arguments += "-YuxiKbId"
    $arguments += $yuxiKbId
    if ($yuxiApiToken) {
        $arguments += "-YuxiApiToken"
        $arguments += $yuxiApiToken
    }
}

if ($aiBaseUrl) {
    $arguments += "-AiBaseUrl"
    $arguments += $aiBaseUrl
}
if ($aiApiKey) {
    $arguments += "-AiApiKey"
    $arguments += $aiApiKey
}
if ($aiModel) {
    $arguments += "-AiModel"
    $arguments += $aiModel
}
if ($aiChatCompletionsPath) {
    $arguments += "-AiChatCompletionsPath"
    $arguments += $aiChatCompletionsPath
}
if ($aiHttpClient) {
    $arguments += "-AiHttpClient"
    $arguments += $aiHttpClient
}
if ($aiTimeoutSeconds) {
    $arguments += "-AiTimeoutSeconds"
    $arguments += $aiTimeoutSeconds
}

Write-Host "Starting RJM stack from $root"
Write-Host "Yuxi API: $yuxiApiBase"
Write-Host "Yuxi KB: $yuxiKbId"
Write-Host "Yuxi token configured: $([bool]$yuxiApiToken)"
Write-Host "AI provider configured: $([bool]($aiBaseUrl -and $aiApiKey -and $aiModel))"
$env:RJM_YUXI_TIMEOUT_SECONDS = $yuxiTimeoutSeconds
& powershell @arguments
