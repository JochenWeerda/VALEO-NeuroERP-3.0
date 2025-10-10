# VALEO NeuroERP - Einfaches Staging-Start-Script
# Startet Infrastruktur in Docker + Backend/Frontend nativ

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  VALEO NeuroERP - Staging (Einfach)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Schritt 1: Infrastruktur starten
Write-Host "Schritt 1: Starte Infrastruktur (Docker)..." -ForegroundColor Yellow
Write-Host "   - PostgreSQL" -ForegroundColor White
Write-Host "   - Redis" -ForegroundColor White
Write-Host "   - Keycloak" -ForegroundColor White
Write-Host ""

docker-compose -f docker-compose.staging-infra.yml up -d

Write-Host "Infrastruktur gestartet!" -ForegroundColor Green
Write-Host ""

# Schritt 2: Warten auf Keycloak
Write-Host "Warte auf Keycloak (~60 Sekunden)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Schritt 3: Anleitung
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  INFRASTRUKTUR LAEUFT!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Laufende Services:" -ForegroundColor Cyan
Write-Host "   PostgreSQL:        localhost:5532" -ForegroundColor Green
Write-Host "   Redis:             localhost:6479" -ForegroundColor Green
Write-Host "   Keycloak:          http://localhost:8180" -ForegroundColor Green
Write-Host "   pgAdmin:           http://localhost:5151" -ForegroundColor Green
Write-Host "   Redis Commander:   http://localhost:8181" -ForegroundColor Green
Write-Host ""

Write-Host "JETZT BACKEND und FRONTEND STARTEN:" -ForegroundColor Cyan
Write-Host ""

Write-Host "Terminal 1 - Backend:" -ForegroundColor Yellow
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 2 - Frontend:" -ForegroundColor Yellow
Write-Host "   cd packages\frontend-web" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""

Write-Host "Nach dem Start:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Backend:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "   Login:    test-admin / Test123!" -ForegroundColor Yellow
Write-Host ""

Write-Host "Tipp: Oeffne 2 separate PowerShell-Fenster" -ForegroundColor Cyan
Write-Host ""
