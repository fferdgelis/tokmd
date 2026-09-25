[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SpecPath,
    [Parameter(Mandatory)][string]$Pbi,
    [string]$OutFile,
    [ValidateSet('deepseek-v4-flash', 'deepseek-v4-pro')]
    [string]$Model = 'deepseek-v4-pro'
)

# Rol TDD del ADR-006: DeepSeek escribe el archivo de test a partir de una
# especificacion que NUNCA incluye la implementacion. Usa el modulo
# compartido C:\IA\modulo-conexion-deepseek tal cual esta, sin tocarlo.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try { Clear-Host } catch { }
Write-Host "=== tokmd: rol TDD (DeepSeek) para $Pbi ===" -ForegroundColor Cyan
Write-Host ""

$totalSteps = 5

Write-Host "[1/$totalSteps] Importando el modulo de conexion DeepSeek..."
Import-Module C:\IA\modulo-conexion-deepseek\DeepSeekConnect.psd1 -Force

Write-Host "[2/$totalSteps] Verificando saldo antes de la llamada..."
$antes = Get-DeepSeekBalance
Write-Host "    Saldo antes: $($antes.Balance) $($antes.Currency)"

Write-Host "[3/$totalSteps] Leyendo la especificacion ($SpecPath)..."
$spec = Get-Content -LiteralPath $SpecPath -Raw -Encoding utf8

Write-Host "[4/$totalSteps] Llamando a DeepSeek ($Model)..."
$systemPrompt = 'You are a meticulous test author working independently from ' +
    'whoever writes the implementation. You have never seen it and never will. ' +
    'Write tests strictly from the given contract and acceptance criteria. ' +
    'Output ONLY what is requested: a single fenced code block, no prose.'
$call = Invoke-DeepSeekChat -Model $Model -MaxTokens 16000 -DisableThinking -Messages @(
    @{ role = 'system'; content = $systemPrompt }
    @{ role = 'user'; content = $spec }
)
Write-Host "    Respuesta en $([math]::Round($call.Seconds,1))s, costo estimado `$$($call.EstimatedCost), reasoning_length=$($call.ReasoningLength), completion_tokens=$($call.Usage.completion_tokens)."

# No se usa Get-CodeFromMarkdown del modulo compartido: su regex no-greedy
# corta en el PRIMER ``` que encuentra, y un test de AC-04 (deteccion de
# encabezados dentro de un bloque de codigo) necesariamente contiene un
# ``` embebido en su propio texto de prueba. Verificado con datos, no
# supuesto: la primera corrida cortaba justo ahi. Extraccion propia: desde
# el primer fence de apertura hasta el ULTIMO ``` de toda la respuesta.
$openMatch = [regex]::Match($call.Content, '```(?:python|py)?\s*\r?\n')
if (-not $openMatch.Success) {
    throw "La respuesta de DeepSeek no tiene un bloque de codigo con fence de apertura."
}
$startIdx = $openMatch.Index + $openMatch.Length
$closeIdx = $call.Content.LastIndexOf('```')
if ($closeIdx -le $startIdx) {
    throw "No se encontro un fence de cierre despues del de apertura."
}
$codigo = $call.Content.Substring($startIdx, $closeIdx - $startIdx).Trim()
if ([string]::IsNullOrWhiteSpace($codigo)) {
    throw "DeepSeek no devolvio un bloque de codigo utilizable."
}

if (-not $OutFile) {
    $OutFile = "tests\test_$($Pbi.ToLower() -replace '^pbi-\d+-?','' -replace '-','_').py"
}
Write-Host "[5/$totalSteps] Guardando en $OutFile..."
$outDir = Split-Path -Parent $OutFile
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}
Set-Content -LiteralPath $OutFile -Value $codigo -Encoding utf8NoBOM

$despues = Get-DeepSeekBalance
Write-Host ""
Write-Host "Listo. Saldo despues: $($despues.Balance) $($despues.Currency) (gasto real: $([math]::Round($antes.Balance - $despues.Balance, 4)))." -ForegroundColor Green
Write-Host "Archivo: $OutFile — revisar antes de correr (rol Desarrollo no debe editarlo, solo diagnosticar)." -ForegroundColor Yellow
