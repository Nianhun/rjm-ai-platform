param(
    [switch]$UseYuxiKnowledge
)

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path "$PSScriptRoot\..\.."
$runtimeDir = Join-Path ([System.IO.Path]::GetTempPath()) ("rjm-java-python-smoke-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $runtimeDir | Out-Null

$pythonExe = "C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$env:PYTHONPATH = Join-Path $projectRoot "apps\ai-engine-python\src"
$env:RJM_FORMULA_PATH = Join-Path $runtimeDir "formula_candidates.jsonl"
$env:RJM_FEEDBACK_PATH = Join-Path $runtimeDir "feedback_events.jsonl"
$env:RJM_SCREENING_PATH = Join-Path $runtimeDir "screening_events.jsonl"

if ($UseYuxiKnowledge) {
    & $pythonExe -m rjm_formula_ai.yuxi_import `
        --yuxi-output "F:\zky\Yuxi-main\output" `
        --out-dir (Join-Path $projectRoot "data\yuxi_import")

    $env:RJM_INGREDIENTS_PATH = Join-Path $projectRoot "data\yuxi_import\ingredients.yuxi.json"
    $env:RJM_RELATIONS_PATH = Join-Path $projectRoot "data\yuxi_import\ingredient_relations.yuxi.json"
    $env:RJM_EVIDENCE_PATH = Join-Path $projectRoot "data\yuxi_import\evidence.yuxi.json"
}

$python = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList "-m", "rjm_formula_ai.http_server" `
    -WorkingDirectory $projectRoot `
    -PassThru `
    -WindowStyle Hidden

try {
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8787/health" -UseBasicParsing -TimeoutSec 1
            if ($response.StatusCode -eq 200) {
                $ready = $true
                break
            }
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }
    if (-not $ready) {
        throw "Python AI HTTP service did not become ready on http://127.0.0.1:8787"
    }

    $mvnArgs = @(
        "test",
        "-Dtest=JavaPythonIntegrationSmokeTests",
        "-Drjm.integration.enabled=true",
        "-Drjm.integration.python-base-url=http://127.0.0.1:8787"
    )
    if ($UseYuxiKnowledge) {
        $mvnArgs += "-Drjm.integration.expect-yuxi=true"
    }

    Push-Location (Join-Path $projectRoot "apps\java-admin-service")
    mvn @mvnArgs
    Pop-Location
} finally {
    if ($python -and -not $python.HasExited) {
        Stop-Process -Id $python.Id -Force
    }
    Remove-Item -LiteralPath $runtimeDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item Env:\RJM_FEEDBACK_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:\RJM_SCREENING_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:\RJM_FORMULA_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:\RJM_INGREDIENTS_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:\RJM_RELATIONS_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:\RJM_EVIDENCE_PATH -ErrorAction SilentlyContinue
}
