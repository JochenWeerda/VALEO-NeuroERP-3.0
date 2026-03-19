$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pidPath = Join-Path $repoRoot "dist/slack-localtunnel.pid"

if (-not (Test-Path $pidPath)) {
    Write-Host "Keine PID-Datei gefunden." -ForegroundColor Yellow
    exit 0
}

$pidValue = (Get-Content -Path $pidPath -Raw).Trim()
if (-not $pidValue) {
    Remove-Item $pidPath -Force
    Write-Host "Leere PID-Datei entfernt." -ForegroundColor Yellow
    exit 0
}

try {
    Stop-Process -Id ([int]$pidValue) -Force -ErrorAction Stop
    Write-Host "Localtunnel mit PID $pidValue gestoppt." -ForegroundColor Green
} catch {
    Write-Host "Prozess $pidValue laeuft nicht mehr." -ForegroundColor Yellow
}

Remove-Item $pidPath -Force

