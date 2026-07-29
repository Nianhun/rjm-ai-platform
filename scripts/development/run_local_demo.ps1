param(
    [switch]$SmokeOnly,
    [switch]$UseYuxiKnowledge,
    [string]$PythonPort = "8000",
    [string]$JavaPort = "8080",
    [string]$ApiToken
)

$ErrorActionPreference = "Stop"
$stackScript = Join-Path $PSScriptRoot "run_prototype_stack.ps1"

$stackArgs = @{
    PythonPort = $PythonPort
    JavaPort = $JavaPort
}
if ($SmokeOnly) {
    $stackArgs["SmokeOnly"] = $true
}
if ($UseYuxiKnowledge) {
    $stackArgs["UseYuxiKnowledge"] = $true
}
if ($ApiToken) {
    $stackArgs["ApiToken"] = $ApiToken
}

& $stackScript @stackArgs
