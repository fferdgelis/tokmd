[CmdletBinding()]
param(
    [string]$RepoRoot = 'C:\IA\Projects\Claude-Tokenizer',
    [string]$DataRoot = 'C:\IA\Data\sonarqube',
    [string]$InfrastructureRoot = 'C:\IA\Projects\framework-multi-ai\devsecops\operations\sonarqube',
    [string]$BaseUrl = 'http://127.0.0.1:9000',
    [string]$ProjectKey = 'tokmd',
    # false solo para el analisis baseline (ADR-005): todavia no hay periodo
    # de codigo nuevo fijado, asi que el gate no mide nada util.
    [bool]$RequireGate = $true
)

# Analisis de SonarQube de tokmd sobre un snapshot limpio de HEAD.
# Patron tomado de whatsapp-mcp/tools/sonarqube/Invoke-SonarAnalysis.ps1 y
# ia-evaluator/orquestador/sonar.py (ADR-005). El checkout real nunca se
# escribe: se analiza `git archive HEAD` en un directorio aparte.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try { Clear-Host } catch { }  # sin consola real (CI, hooks) no hay que limpiar
Write-Host "=== tokmd: SonarQube Quality Gate ===" -ForegroundColor Cyan
Write-Host "Analiza un snapshot de HEAD y exige el Quality Gate en OK (salvo -RequireGate:`$false)." -ForegroundColor Cyan
Write-Host ""

$totalSteps = 8
$scannerImage = 'sonarsource/sonar-scanner-cli:12.1.0.3233_8.0.1'
$snapshotDir = $null
$reportsDir = $null

try {
    Write-Host "[1/$totalSteps] Leyendo el automation-token de la boveda DPAPI..."
    Import-Module (Join-Path $InfrastructureRoot 'SonarQube.Dpapi.psm1') -Force
    $secrets = Get-SonarQubeSecrets -DataRoot $DataRoot
    $token = $secrets.AutomationToken
    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "El automation-token vino vacio de la boveda DPAPI."
    }
    $authHeader = New-SonarQubeTokenAuthorizationHeader -Token $token

    Write-Host "[2/$totalSteps] Creando el proyecto '$ProjectKey' en Sonar (idempotente)..."
    try {
        Invoke-RestMethod -Uri "$BaseUrl/api/projects/create" -Method Post -Headers $authHeader `
            -Body @{ project = $ProjectKey; name = $ProjectKey } -TimeoutSec 30 | Out-Null
        Write-Host "    Proyecto creado."
    } catch {
        # PowerShell 7: Invoke-RestMethod expone el cuerpo del error en
        # ErrorDetails.Message (HttpResponseMessage no tiene GetResponseStream,
        # eso es .NET Framework / Windows PowerShell 5.1).
        $detalle = $_.ErrorDetails.Message
        if ($detalle -and $detalle -match 'already exists') {
            Write-Host "    Ya existia."
        } else {
            throw "projects/create fallo: $detalle"
        }
    }

    Write-Host "[3/$totalSteps] Contando analisis previos publicados..."
    $previos = (Invoke-RestMethod -Uri "$BaseUrl/api/project_analyses/search?project=$ProjectKey&ps=1" -Headers $authHeader -TimeoutSec 30).paging.total
    Write-Host "    Analisis previos: $previos"

    Write-Host "[4/$totalSteps] Armando el snapshot de HEAD con git archive..."
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $snapshotDir = Join-Path $DataRoot "scratch\tokmd-$stamp"
    $reportsDir = Join-Path $DataRoot "reports\tokmd\$stamp"
    New-Item -ItemType Directory -Force -Path $snapshotDir | Out-Null
    New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
    # Se extrae por zip, no por `git archive HEAD | tar -x -C <dir>`: cuando el
    # `tar` que gana en el PATH es el de Git (MSYS, C:\Program Files\Git\usr\bin)
    # y no el de Windows (System32), MSYS traduce la ruta absoluta con `\` y el
    # comando muere con "Cannot open: No such file or directory". Que funcione o
    # no dependia del orden del PATH de la consola: el zip no depende de nada.
    $zipPath = Join-Path $DataRoot "scratch\tokmd-$stamp.zip"
    Push-Location $RepoRoot
    try {
        $commit = (git rev-parse --short HEAD).Trim()
        git archive --format=zip -o $zipPath HEAD
        if ($LASTEXITCODE -ne 0) { throw "git archive HEAD fallo (codigo $LASTEXITCODE)." }
    } finally {
        Pop-Location
    }
    Expand-Archive -LiteralPath $zipPath -DestinationPath $snapshotDir -Force
    Remove-Item -LiteralPath $zipPath -Force
    Write-Host "    Snapshot de commit $commit en $snapshotDir"

    Write-Host "[5/$totalSteps] Corriendo pytest con cobertura dentro del snapshot..."
    Push-Location $snapshotDir
    try {
        uv sync 2>&1 | Out-String | Write-Host
        if ($LASTEXITCODE -ne 0) { throw "uv sync fallo dentro del snapshot." }
        uv run pytest --cov=src/tokmd --cov-report="xml:$reportsDir\coverage.xml" 2>&1 | Out-String | Write-Host
        if ($LASTEXITCODE -ne 0) { throw "pytest fallo dentro del snapshot; el escaner no se ejecuta." }
    } finally {
        Pop-Location
    }
    if (-not (Test-Path -LiteralPath (Join-Path $reportsDir 'coverage.xml'))) {
        throw "pytest no produjo coverage.xml en $reportsDir."
    }

    Write-Host "[6/$totalSteps] Corriendo el escaner de SonarQube (Docker)..."
    $argv = @(
        'run', '--rm',
        '--network', 'local-sonarqube-network',
        '--env', "SONAR_HOST_URL=http://sonarqube:9000",
        '--env', 'SONAR_TOKEN',
        '--mount', "type=bind,source=$snapshotDir,target=/usr/src,readonly",
        '--mount', "type=bind,source=$reportsDir,target=/reports,readonly",
        '--workdir', '/usr/src',
        $scannerImage,
        "-Dproject.settings=/usr/src/tools/sonarqube/sonar-project.properties",
        "-Dsonar.projectVersion=$commit",
        '-Dsonar.qualitygate.wait=true'
    )
    $scannerLog = Join-Path $reportsDir 'scanner.log'
    $env:SONAR_TOKEN = $token
    & docker @argv *>&1 | Tee-Object -FilePath $scannerLog | Out-Null
    $scannerExit = $LASTEXITCODE
    $env:SONAR_TOKEN = $null
    if ($scannerExit -ne 0) {
        Write-Host "    Escaner devolvio codigo $scannerExit. Ultimas lineas del log ($scannerLog):" -ForegroundColor Yellow
        Get-Content -LiteralPath $scannerLog -Tail 40 | ForEach-Object { Write-Host "    $_" }
        if ($RequireGate) {
            throw "El escaner o el Quality Gate fallaron (codigo $scannerExit)."
        }
    }

    Write-Host "[7/$totalSteps] Esperando que el analisis quede publicado..."
    $limite = (Get-Date).AddSeconds(180)
    $publicado = $false
    while ((Get-Date) -lt $limite) {
        $total = (Invoke-RestMethod -Uri "$BaseUrl/api/project_analyses/search?project=$ProjectKey&ps=1" -Headers $authHeader -TimeoutSec 30).paging.total
        if ($total -gt $previos) { $publicado = $true; break }
        Start-Sleep -Seconds 3
    }
    if (-not $publicado) { throw "El analisis no se publico a tiempo (180s)." }

    Write-Host "[8/$totalSteps] Leyendo el Quality Gate..."
    $estado = Invoke-RestMethod -Uri "$BaseUrl/api/qualitygates/project_status?projectKey=$ProjectKey" -Headers $authHeader -TimeoutSec 30
    $gate = $estado.projectStatus.status
    $evidencia = [ordered]@{
        projectKey = $ProjectKey
        commit     = $commit
        timestamp  = $stamp
        gate       = $gate
        conditions = $estado.projectStatus.conditions
    }
    $evidenciaPath = Join-Path $reportsDir 'gate-status.json'
    ($evidencia | ConvertTo-Json -Depth 6) | Out-File -LiteralPath $evidenciaPath -Encoding utf8
    Write-Host "    Quality Gate: $gate (evidencia: $evidenciaPath)"

    if ($RequireGate -and $gate -ne 'OK') {
        throw "Quality Gate en '$gate', no 'OK'. Evidencia en $evidenciaPath."
    }

    Write-Host ""
    Write-Host "Gate: $gate. Evidencia en $reportsDir." -ForegroundColor Green
}
finally {
    if ($snapshotDir -and (Test-Path -LiteralPath $snapshotDir)) {
        # Borrado seguro: sólo si cuelga exactamente de DataRoot\scratch y un
        # nivel por debajo (mismo principio que whatsapp-mcp).
        $scratchRoot = [System.IO.Path]::GetFullPath((Join-Path $DataRoot 'scratch'))
        $full = [System.IO.Path]::GetFullPath($snapshotDir)
        $parent = [System.IO.Path]::GetFullPath((Split-Path -Parent $full))
        if ($parent -eq $scratchRoot -and $full.StartsWith($scratchRoot)) {
            Remove-Item -LiteralPath $snapshotDir -Recurse -Force
        } else {
            Write-Host "No se borro '$snapshotDir': no cumple la forma esperada." -ForegroundColor Yellow
        }
    }
}
