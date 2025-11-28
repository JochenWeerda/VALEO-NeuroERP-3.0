# ============================================================================
# VALEO-NeuroERP - Setup Service Migrations
# Kopiert Entrypoint-Scripts zu allen CRM-Services
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "🔧 VALEO-NeuroERP - Service Migration Setup" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Services mit Alembic-Migrationen
$Services = @(
    @{ Name = "crm-core"; Port = 5600 }
    @{ Name = "crm-sales"; Port = 5700 }
    @{ Name = "crm-service"; Port = 5800 }
    @{ Name = "crm-workflow"; Port = 5900 }
    @{ Name = "crm-analytics"; Port = 6000 }
    @{ Name = "crm-communication"; Port = 6100 }
    @{ Name = "crm-ai"; Port = 6200 }
    @{ Name = "crm-multichannel"; Port = 6300 }
    @{ Name = "crm-marketing"; Port = 6400 }
    @{ Name = "crm-consent"; Port = 6500 }
    @{ Name = "crm-gdpr"; Port = 6600 }
    @{ Name = "inventory"; Port = 5400 }
)

$TemplatePath = "scripts/templates/crm-service-entrypoint.sh"
$TemplateContent = Get-Content $TemplatePath -Raw

foreach ($Service in $Services) {
    $ServicePath = "services/$($Service.Name)"
    $EntrypointPath = "$ServicePath/docker-entrypoint.sh"
    $DockerfilePath = "$ServicePath/Dockerfile"
    $AlembicIni = "$ServicePath/alembic.ini"
    
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "📦 Service: $($Service.Name)" -ForegroundColor White
    
    if (-not (Test-Path $ServicePath)) {
        Write-Host "   ⏭️  Service-Verzeichnis nicht gefunden" -ForegroundColor DarkGray
        continue
    }
    
    if (-not (Test-Path $AlembicIni)) {
        Write-Host "   ⏭️  Keine Alembic-Konfiguration" -ForegroundColor DarkGray
        continue
    }
    
    # Kopiere Entrypoint-Script (mit Service-spezifischen Anpassungen)
    $CustomContent = $TemplateContent -replace 'SERVICE_PORT:-5600', "SERVICE_PORT:-$($Service.Port)"
    $CustomContent = $CustomContent -replace 'SERVICE_NAME:-crm-service', "SERVICE_NAME:-$($Service.Name)"
    
    Set-Content -Path $EntrypointPath -Value $CustomContent -NoNewline
    Write-Host "   ✅ Entrypoint-Script erstellt" -ForegroundColor Green
    
    # Prüfe und aktualisiere Dockerfile
    if (Test-Path $DockerfilePath) {
        $DockerfileContent = Get-Content $DockerfilePath -Raw
        
        if ($DockerfileContent -notmatch "docker-entrypoint.sh") {
            Write-Host "   ⚠️  Dockerfile muss manuell angepasst werden!" -ForegroundColor Yellow
            Write-Host "      Füge hinzu:" -ForegroundColor DarkGray
            Write-Host "        COPY docker-entrypoint.sh ./docker-entrypoint.sh" -ForegroundColor DarkGray
            Write-Host "        RUN chmod +x ./docker-entrypoint.sh" -ForegroundColor DarkGray
            Write-Host "        ENTRYPOINT [""./docker-entrypoint.sh""]" -ForegroundColor DarkGray
        } else {
            Write-Host "   ✅ Dockerfile bereits konfiguriert" -ForegroundColor Green
        }
    }
    
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "✅ Setup abgeschlossen!" -ForegroundColor Green
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Yellow
Write-Host "1. Dockerfiles anpassen (falls nötig)" -ForegroundColor DarkGray
Write-Host "2. Container neu bauen: docker-compose build" -ForegroundColor DarkGray
Write-Host "3. Container starten: docker-compose up -d" -ForegroundColor DarkGray

