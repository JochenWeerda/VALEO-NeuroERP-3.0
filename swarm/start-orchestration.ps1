***REMOVED*** Start Orchestration für GAP-Schließung
***REMOVED*** Option 3: Vollständige Implementierung mit 4 parallelen Agenten

Write-Host "🎼 VALEO NeuroERP - GAP-Schließung Orchestrierung" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Prüfe Python
Write-Host "🔍 Prüfe Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python gefunden: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python nicht gefunden. Bitte Python installieren." -ForegroundColor Red
    exit 1
}

***REMOVED*** Prüfe Verzeichnisse
Write-Host "🔍 Prüfe Verzeichnisse..." -ForegroundColor Yellow
$swarmPath = "swarm"
$statusPath = "$swarmPath\status"
$handoffsPath = "$swarmPath\handoffs"

if (-not (Test-Path $swarmPath)) {
    New-Item -ItemType Directory -Path $swarmPath -Force | Out-Null
}
if (-not (Test-Path $statusPath)) {
    New-Item -ItemType Directory -Path $statusPath -Force | Out-Null
}
if (-not (Test-Path $handoffsPath)) {
    New-Item -ItemType Directory -Path $handoffsPath -Force | Out-Null
}
Write-Host "✅ Verzeichnisse vorhanden" -ForegroundColor Green

***REMOVED*** Initialisiere Orchestrator
Write-Host ""
Write-Host "🎼 Initialisiere Orchestrator..." -ForegroundColor Yellow
python swarm\orchestrator.py --init
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Orchestrator-Initialisierung fehlgeschlagen" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Orchestrator initialisiert" -ForegroundColor Green
Write-Host ""

***REMOVED*** Zeige nächste Schritte
Write-Host "📋 Nächste Schritte:" -ForegroundColor Cyan
Write-Host "1. Sprint 1 starten: python swarm\orchestrator.py --sprint-start 1" -ForegroundColor White
Write-Host "2. Agenten starten (siehe swarm\missions\gap-closure-orchestration.md)" -ForegroundColor White
Write-Host "3. Status prüfen: python swarm\orchestrator.py --report" -ForegroundColor White
Write-Host ""
Write-Host "📚 Dokumentation:" -ForegroundColor Cyan
Write-Host "- Orchestrierung: swarm\missions\gap-closure-orchestration.md" -ForegroundColor White
Write-Host "- Agent-Zuordnung: swarm\missions\agent-assignments.md" -ForegroundColor White
Write-Host "- Dashboard: swarm\status\orchestrator-dashboard.md" -ForegroundColor White
Write-Host ""

