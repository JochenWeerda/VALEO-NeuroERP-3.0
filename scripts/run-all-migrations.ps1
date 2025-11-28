***REMOVED*** ============================================================================
***REMOVED*** VALEO-NeuroERP - MASTER MIGRATION SCRIPT (PowerShell)
***REMOVED*** Führt alle Alembic-Migrationen für alle CRM-Services aus
***REMOVED*** ============================================================================

$ErrorActionPreference = "Continue"

Write-Host "🗄️  VALEO-NeuroERP Database Migration Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Liste aller Services mit Alembic-Migrationen
$SERVICES = @(
    "crm-core"
    "crm-sales"
    "crm-service"
    "crm-workflow"
    "crm-analytics"
    "crm-communication"
    "crm-multichannel"
    "crm-marketing"
    "crm-ai"
    "crm-consent"
    "crm-gdpr"
    "inventory"
)

***REMOVED*** Zähler
$SuccessCount = 0
$ErrorCount = 0
$SkippedCount = 0

Write-Host "📋 Starte Migrationen für $($SERVICES.Count) Services..." -ForegroundColor Yellow
Write-Host ""

foreach ($SERVICE in $SERVICES) {
    $ContainerName = "valeo-neuro-erp-${SERVICE}-1"
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "🔧 Service: $SERVICE" -ForegroundColor White
    
    ***REMOVED*** Prüfe ob Container läuft
    $ContainerRunning = docker ps --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
    
    if (-not $ContainerRunning) {
        ***REMOVED*** Versuche alternativen Container-Namen
        $ContainerName = "valeo-neuro-erp-$($SERVICE.Replace('-', ''))"
        $ContainerRunning = docker ps --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
    }
    
    if ($ContainerRunning) {
        Write-Host "   📦 Container gefunden: $ContainerRunning" -ForegroundColor Green
        
        ***REMOVED*** Führe Migration aus
        Write-Host "   ⬆️  Führe Migration aus..." -ForegroundColor Yellow
        
        try {
            $result = docker exec $ContainerRunning alembic upgrade head 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ Migration erfolgreich!" -ForegroundColor Green
                $SuccessCount++
            } else {
                Write-Host "   ❌ Migration fehlgeschlagen: $result" -ForegroundColor Red
                $ErrorCount++
            }
        } catch {
            Write-Host "   ❌ Fehler: $_" -ForegroundColor Red
            $ErrorCount++
        }
    } else {
        Write-Host "   ⏭️  Container nicht gestartet" -ForegroundColor DarkGray
        $SkippedCount++
    }
    
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📊 ZUSAMMENFASSUNG" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "   ✅ Erfolgreich:  $SuccessCount" -ForegroundColor Green
Write-Host "   ⏭️  Übersprungen: $SkippedCount" -ForegroundColor DarkGray
Write-Host "   ❌ Fehler:       $ErrorCount" -ForegroundColor Red
Write-Host ""

if ($ErrorCount -gt 0) {
    Write-Host "⚠️  Einige Migrationen sind fehlgeschlagen!" -ForegroundColor Yellow
} else {
    Write-Host "🎉 Alle Migrationen abgeschlossen!" -ForegroundColor Green
}

