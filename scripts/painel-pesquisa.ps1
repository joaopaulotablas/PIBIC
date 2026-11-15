param(
    [string]$Banco = "data/bpc-consolidado-luna-20261007.sqlite",
    [int]$Porta = 8000
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$databaseFile = if ([System.IO.Path]::IsPathRooted($Banco)) { $Banco } else { Join-Path $projectRoot $Banco }
if (-not (Test-Path -LiteralPath $databaseFile -PathType Leaf)) { throw "Banco não encontrado: $databaseFile" }
$databaseFile = (Resolve-Path -LiteralPath $databaseFile).Path
$pythonExe = Join-Path $projectRoot ".venv/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $pythonExe)) { throw "Ambiente Python ausente: $pythonExe" }
$previousDatabase = $env:DATABASE_URL
try {
    $env:DATABASE_URL = "sqlite:///" + ($databaseFile -replace '\\', '/')
    Write-Host "Banco: $databaseFile"
    Write-Host "Painel: http://127.0.0.1:$Porta/admin/analise"
    Write-Host "Ctrl+C para encerrar. Revisões são gravadas neste banco."
    & $pythonExe -m uvicorn bpc_ingestion.api:app --host 127.0.0.1 --port $Porta
} finally {
    $env:DATABASE_URL = $previousDatabase
}
