[CmdletBinding()]
param(
    [string]$DataRoot = 'C:\IA\Data\sonarqube',
    [string]$InfrastructureRoot = 'C:\IA\Projects\framework-multi-ai\devsecops\operations\sonarqube',
    [string]$BaseUrl = 'http://127.0.0.1:9000',
    [string]$ProjectKeyPrefix = 'tokmd-negative-fixture'
)

# Canario de PBI-002 (punto 2 de las "Dos cosas a corregir" del traspaso
# 20260925): probar que el Quality Gate de Sonar SI puede dar ERROR antes de
# confiar en que el gate de `tokmd` mide algo real. Patron tomado tal cual de
# whatsapp-mcp/tools/sonarqube/Test-QualityGateFailure.ps1, con un projectKey
# propio ('tokmd-negative-fixture', no 'sonarqube-negative-fixture') para no
# compartir estado con el canario de otro proyecto en el mismo servidor Sonar.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $InfrastructureRoot 'SonarQube.Dpapi.psm1') -Force

function Invoke-NegativeScanner {
    param(
        [Parameter(Mandatory)][string]$SourceDirectory,
        [Parameter(Mandatory)][string]$Token,
        [Parameter(Mandatory)][string]$LogPath
    )

    $previousToken = [Environment]::GetEnvironmentVariable('SONAR_TOKEN', 'Process')
    try {
        [Environment]::SetEnvironmentVariable('SONAR_TOKEN', $Token, 'Process')
        $output = & docker run --rm `
            --network local-sonarqube-network `
            --env 'SONAR_HOST_URL=http://sonarqube:9000' `
            --env SONAR_TOKEN `
            --mount "type=bind,source=$SourceDirectory,target=/usr/src,readonly" `
            --workdir /usr/src `
            sonarsource/sonar-scanner-cli:12.1.0.3233_8.0.1 '-Dsonar.working.directory=/tmp/sonar-work' 2>&1
        $exitCode = $LASTEXITCODE
        $output | ForEach-Object ToString | Set-Content -LiteralPath $LogPath -Encoding utf8NoBOM
        return $exitCode
    } finally {
        [Environment]::SetEnvironmentVariable('SONAR_TOKEN', $previousToken, 'Process')
    }
}

$secrets = Get-SonarQubeSecrets -DataRoot $DataRoot
$headers = New-SonarQubeTokenAuthorizationHeader -Token $secrets.AutomationToken
$nonce = [Guid]::NewGuid().ToString('N')
# Clave unica por corrida: un proyecto auto-provisionado por el escaner (sin
# projects/create previo) deja al token sin permiso 'Administer' sobre si
# mismo -> new_code_periods/set falla con "Insufficient privileges", y esa
# clave queda huerfana para siempre (medido en tokmd el 25/09/2026, con
# 'tokmd-negative-fixture' a secas). El projects/create explicito de abajo
# evita que vuelva a pasar, pero no rescata una clave ya huerfana.
$ProjectKey = "$ProjectKeyPrefix-$($nonce.Substring(0,8))"
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) "tokmd-negative-$nonce"
$violationFile = "uncovered-$nonce.py"
$reportRoot = Join-Path $DataRoot 'reports\tokmd-negative-gate'
$reportPath = Join-Path $reportRoot ("negative-" + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '.json')
$baselineExit = $null
$scanExit = $null
$gateStatus = $null
[void](New-Item -ItemType Directory -Path $tempRoot)
[void](New-Item -ItemType Directory -Path $reportRoot -Force)

try {
    # Creacion explicita del proyecto ANTES de escanear: un proyecto
    # auto-provisionado por el escaner (sin este paso) no le da al token
    # automation-token permiso 'Administer' sobre si mismo, y
    # new_code_periods/set lo exige -> "Insufficient privileges" (medido en
    # tokmd el 25/09/2026). Mismo patron que Invoke-SonarGate.ps1.
    try {
        Invoke-RestMethod -Uri "$BaseUrl/api/projects/create" -Method Post -Headers $headers `
            -Body @{ project = $ProjectKey; name = $ProjectKey } -TimeoutSec 30 | Out-Null
    } catch {
        $detalle = $_.ErrorDetails.Message
        if (-not ($detalle -and $detalle -match 'already exists')) {
            throw "projects/create fallo: $detalle"
        }
    }

    @(
        "sonar.projectKey=$ProjectKey",
        'sonar.projectName=tokmd controlled Quality Gate failure',
        'sonar.sources=.',
        'sonar.sourceEncoding=UTF-8',
        'sonar.python.version=3.12',
        'sonar.qualitygate.wait=true',
        'sonar.qualitygate.timeout=300'
    ) | Set-Content -LiteralPath (Join-Path $tempRoot 'sonar-project.properties') -Encoding utf8NoBOM

    @(
        '"""Safe baseline for a controlled Quality Gate failure."""',
        '',
        'def baseline(value):',
        '    return value'
    ) | Set-Content -LiteralPath (Join-Path $tempRoot 'baseline.py') -Encoding utf8NoBOM

    $baselineExit = Invoke-NegativeScanner -SourceDirectory $tempRoot -Token $secrets.AutomationToken -LogPath (Join-Path $reportRoot "$ProjectKey-baseline.log")
    if ($baselineExit -ne 0) { throw "El baseline controlado falló con código $baselineExit." }

    $baselineAnalyses = Invoke-RestMethod -Uri "$BaseUrl/api/project_analyses/search?project=$ProjectKey&ps=1" -Headers $headers
    if (@($baselineAnalyses.analyses).Count -eq 0) { throw 'SonarQube no publicó el baseline controlado.' }
    Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/new_code_periods/set" -Headers $headers -Body @{
        project = $ProjectKey
        type = 'SPECIFIC_ANALYSIS'
        value = [string]$baselineAnalyses.analyses[0].key
    } | Out-Null

    @(
        '"""Synthetic fixture: intentionally violates active Python rules for a negative gate test."""',
        '',
        'def BadFunctionName(unused_parameter):',
        '    unused_local = 1',
        '    print("negative gate fixture")',
        '    raise'
    ) | Set-Content -LiteralPath (Join-Path $tempRoot $violationFile) -Encoding utf8NoBOM

    $scanExit = Invoke-NegativeScanner -SourceDirectory $tempRoot -Token $secrets.AutomationToken -LogPath (Join-Path $reportRoot "$ProjectKey-scanner.log")
    $gate = Invoke-RestMethod -Uri "$BaseUrl/api/qualitygates/project_status?projectKey=$ProjectKey" -Headers $headers
    $gateStatus = [string]$gate.projectStatus.status
    [ordered]@{
        checkedUtc = [DateTime]::UtcNow.ToString('o')
        projectKey = $ProjectKey
        baselineScannerExitCode = $baselineExit
        scannerExitCode = $scanExit
        gateStatus = $gateStatus
        expectedScannerFailure = $true
        passed = ($baselineExit -eq 0 -and $scanExit -ne 0 -and $gateStatus -eq 'ERROR')
        conditions = $gate.projectStatus.conditions
    } | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $reportPath -Encoding utf8NoBOM

    if ($baselineExit -ne 0 -or $scanExit -eq 0 -or $gateStatus -ne 'ERROR') {
        throw "La prueba negativa no rechazó el fixture: baseline=$baselineExit, exit=$scanExit, gate=$gateStatus"
    }
} finally {
    $resolvedTemp = [IO.Path]::GetFullPath($tempRoot)
    $systemTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($resolvedTemp.StartsWith($systemTemp, [StringComparison]::OrdinalIgnoreCase) -and
        [IO.Path]::GetFileName($resolvedTemp) -eq "tokmd-negative-$nonce" -and
        (Test-Path -LiteralPath $resolvedTemp)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}

Write-Host "Prueba negativa correcta: baseline=$baselineExit, scanner=$scanExit, gate=$gateStatus"
Write-Output $reportPath
exit 0
