# PowerShell Script zum Starten des Swarm-Systems
# Usage: .\swarm\start-swarm.ps1

Write-Host "🚀 Valero NeuroERP - Swarm System Start" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob Docker läuft
Write-Host "📋 Prüfe Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker läuft" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker läuft nicht! Bitte starte Docker Desktop." -ForegroundColor Red
    exit 1
}

# Prüfe ob .env.swarm existiert
if (-not (Test-Path ".env.swarm")) {
    Write-Host "⚠️  .env.swarm nicht gefunden. Erstelle Standard-Datei..." -ForegroundColor Yellow
    @"
NEUROERP_URL=http://localhost:3000
NEUROERP_USER=admin
NEUROERP_PASS=admin123
"@ | Out-File -FilePath ".env.swarm" -Encoding UTF8
    Write-Host "✅ .env.swarm erstellt" -ForegroundColor Green
}

# Lade .env.swarm
Write-Host "📝 Lade Umgebungsvariablen aus .env.swarm..." -ForegroundColor Yellow
Get-Content ".env.swarm" | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
        Write-Host "  $key = $value" -ForegroundColor Gray
    }
}

# Prüfe ob Frontend bereits läuft
$frontendUrl = $env:NEUROERP_URL
if (-not $frontendUrl) {
    $frontendUrl = "http://localhost:3000"
}

Write-Host ""
Write-Host "🔍 Prüfe ob Frontend auf $frontendUrl erreichbar ist..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$frontendUrl/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend läuft bereits auf $frontendUrl" -ForegroundColor Green
        $useExistingFrontend = $true
    }
} catch {
    Write-Host "⚠️  Frontend nicht erreichbar. Starte neues Frontend im Swarm..." -ForegroundColor Yellow
    $useExistingFrontend = $false
}

# Starte Services
Write-Host ""
Write-Host "🐳 Starte Docker Compose Services..." -ForegroundColor Cyan

if ($useExistingFrontend) {
    Write-Host "  → Nutze bestehendes Frontend" -ForegroundColor Gray
    Write-Host "  → Starte nur Tests und UI-Explorer" -ForegroundColor Gray
    docker compose -f docker-compose.swarm.yml up -d neuroerp-tests neuroerp-ui-explorer
} else {
    Write-Host "  → Starte Frontend + Tests + UI-Explorer" -ForegroundColor Gray
    docker compose -f docker-compose.swarm.yml up -d
}

Write-Host ""
Write-Host "⏳ Warte auf Services..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Zeige Status
Write-Host ""
Write-Host "📊 Service-Status:" -ForegroundColor Cyan
docker compose -f docker-compose.swarm.yml ps

Write-Host ""
Write-Host "📝 Logs anzeigen:" -ForegroundColor Cyan
Write-Host "  docker compose -f docker-compose.swarm.yml logs -f" -ForegroundColor Gray

Write-Host ""
Write-Host "🛑 Services stoppen:" -ForegroundColor Cyan
Write-Host "  docker compose -f docker-compose.swarm.yml down" -ForegroundColor Gray

Write-Host ""
Write-Host "✅ Swarm-System gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Cyan
Write-Host "  1. Prüfe Logs: docker compose -f docker-compose.swarm.yml logs -f" -ForegroundColor White
Write-Host "  2. UI-Explorer Output: evidence/screenshots/" -ForegroundColor White
Write-Host "  3. Test-Results: evidence/traces/" -ForegroundColor White
Write-Host ""

