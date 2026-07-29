param(
    [switch]$SmokeOnly,
    [string]$JavaPort = "8080"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path "$PSScriptRoot\..\.."
$javaDir = Join-Path $root "apps\java-admin-service"
$runtimeDir = Join-Path $root "data\runtime\java-db"
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

if ($SmokeOnly) {
    Push-Location $javaDir
    try {
        mvn "-Dtest=DbLocalDataSourceConfigTests,DbModeH2IntegrationTests" test
    } finally {
        Pop-Location
    }
    exit 0
}

$arguments = "--server.port=$JavaPort --spring.profiles.active=db-local"
Push-Location $javaDir
try {
    mvn spring-boot:run "-Dspring-boot.run.arguments=$arguments"
} finally {
    Pop-Location
}
