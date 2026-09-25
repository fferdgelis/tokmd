[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SnapshotDir,
    [Parameter(Mandatory)][string]$BriefPath,
    [Parameter(Mandatory)][string]$OutputPath,
    [string]$Modelo = 'openrouter/moonshotai/kimi-k3'
)

# QA independiente (ADR-005/ADR-006): Kimi K3 via OpenCode, sobre un snapshot
# de un commit ya gateado por Sonar. El encargo se pasa por RUTA en el texto,
# nunca con -f (esa bandera es para listas de archivos y se come el mensaje
# como si fuera otro archivo — leccion de framework-multi-ai, 21/09/2026).
# El aislamiento read-only es de convencion (la instruccion del brief), igual
# que en el precedente verificado: OpenCode no se reconfigura por corrida.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try { Clear-Host } catch { }
Write-Host "=== tokmd: QA independiente (Kimi K3 / OpenCode) ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path -LiteralPath $BriefPath)) { throw "No existe el brief: $BriefPath" }
if (-not (Test-Path -LiteralPath $SnapshotDir)) { throw "No existe el snapshot: $SnapshotDir" }

$mensaje = "Primero abri y lee este archivo con tu herramienta de lectura, es el encargo completo: $BriefPath"

Write-Host "Modelo   : $Modelo"
Write-Host "Snapshot : $SnapshotDir"
Write-Host "Brief    : $BriefPath"
Write-Host ""

$reloj = [Diagnostics.Stopwatch]::StartNew()
$respuesta = & opencode run -m $Modelo --dir $SnapshotDir $mensaje 2>&1
$codigo = $LASTEXITCODE
$reloj.Stop()

$texto = ($respuesta | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
Set-Content -LiteralPath $OutputPath -Value $texto -Encoding utf8NoBOM

Write-Host "Codigo de salida: $codigo. Duracion: $([math]::Round($reloj.Elapsed.TotalSeconds,1))s."
Write-Host "Respuesta guardada en: $OutputPath"
