# VALEO NeuroERP PostgreSQL Connectivity Fix Script
# =================================================
# This script fixes the PostgreSQL connectivity issues in Docker Desktop

param(
    [switch]$DryRun = $false,
    [switch]$CreateMissingSchemas = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "VALEO NeuroERP PostgreSQL Fix Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Colors
$Green = [ConsoleColor]::Green
$Yellow = [ConsoleColor]::Yellow
$Red = [ConsoleColor]::Red
$Cyan = [ConsoleColor]::Cyan

function Test-Command {
    param($cmd)
    try {
        Get-Command $cmd -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Prüfe Voraussetzungen..." -ForegroundColor $Cyan

if (-not (Test-Command "docker")) {
    Write-Host "FEHLER: Docker ist nicht installiert oder nicht im PATH" -ForegroundColor $Red
    exit 1
}

# Check if PostgreSQL container exists
$postgresContainer = docker ps -a --filter "name=postgres" --format "{{.Names}}" | Where-Object { $_ -match "valeo" }
if (-not $postgresContainer) {
    Write-Host "FEHLER: PostgreSQL Container nicht gefunden" -ForegroundColor $Red
    exit 1
}

Write-Host "Gefundener PostgreSQL Container: $postgresContainer" -ForegroundColor $Green

# Step 1: Check and fix network connectivity
Write-Host ""
Write-Host "Schritt 1: Prüfe Netzwerk-Konnektivität..." -ForegroundColor $Cyan

$postgresNetworks = docker inspect $postgresContainer --format "{{json .NetworkSettings.Networks}}" | ConvertFrom-Json
$backendContainer = "valeo-neuro-erp-backend"

# Check if postgres is on valeo-network
$needsNetworkFix = $false
if ($postgresNetworks.PSObject.Properties.Name -notcontains "valeo-neuro-erp_valeo-network") {
    $needsNetworkFix = $true
    Write-Host "  PostgreSQL ist NICHT im valeonetzwerk!" -ForegroundColor $Yellow
} else {
    Write-Host "  PostgreSQL ist bereits im valeonetzwerk" -ForegroundColor $Green
}

if ($DryRun) {
    if ($needsNetworkFix) {
        Write-Host "  [DRY-RUN] Würde Netzwerk verbinden: valeo-neuro-erp_valeo-network" -ForegroundColor $Yellow
    }
} else {
    if ($needsNetworkFix) {
        Write-Host "  Verbinde PostgreSQL mit valeonetzwerk..." -ForegroundColor $Cyan
        try {
            docker network connect valeo-neuro-erp_valeo-network $postgresContainer
            Write-Host "  Netzwerk erfolgreich verbunden!" -ForegroundColor $Green
        } catch {
            Write-Host "  FEHLER beim Verbinden des Netzwerks: $_" -ForegroundColor $Red
        }
    }
}

# Step 2: Verify connection from backend
Write-Host ""
Write-Host "Schritt 2: Prüfe Verbindung vom Backend..." -ForegroundColor $Cyan

$connectionTest = docker exec $backendContainer sh -c "nc -zv postgres 5432" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Verbindung erfolgreich: $connectionTest" -ForegroundColor $Green
} else {
    Write-Host "  VERBINDUNG FEHLGESCHLAGEN: $connectionTest" -ForegroundColor $Red
}

# Step 3: Test database connection
Write-Host ""
Write-Host "Schritt 3: Prüfe Datenbank-Verbindung..." -ForegroundColor $Cyan

$dbTest = docker exec $postgresContainer psql -U valeo_dev -d valeo_neuro_erp -c "SELECT 1 AS test;" 2>&1
if ($dbTest -match "1 row") {
    Write-Host "  Datenbank-Verbindung erfolgreich!" -ForegroundColor $Green
} else {
    Write-Host "  DATENBANK-FEHLER: $dbTest" -ForegroundColor $Red
}

# Step 4: Create missing schemas (optional)
if ($CreateMissingSchemas) {
    Write-Host ""
    Write-Host "Schritt 4: Erstelle fehlende Schemas..." -ForegroundColor $Cyan

    $schemas = @("domain_inventory", "domain_agrar", "domain_sales", "domain_finance", "domain_hr")
    
    foreach ($schema in $schemas) {
        $exists = docker exec $postgresContainer psql -U valeo_dev -d valeo_neuro_erp -t -c "SELECT 1 FROM information_schema.schemata WHERE schema_name = '$schema';" 2>&1
        if ($exists -notmatch "1") {
            Write-Host "  Erstelle Schema: $schema" -ForegroundColor $Yellow
            docker exec $postgresContainer psql -U valeo_dev -d valeo_neuro_erp -c "CREATE SCHEMA IF NOT EXISTS $schema; GRANT ALL ON SCHEMA $schema TO valeo_dev;" 2>&1
        } else {
            Write-Host "  Schema existiert bereits: $schema" -ForegroundColor $Green
        }
    }
}

# Step 5: Summary
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Zusammenfassung" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Container: $postgresContainer" -ForegroundColor White
Write-Host "Netzwerk-Problem behoben: $(-not $needsNetworkFix)" -ForegroundColor $(if ($needsNetworkFix) { $Yellow } else { $Green })

Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor $Cyan
Write-Host "1. Starten Sie die Container neu:" -ForegroundColor White
Write-Host "   docker-compose restart backend postgres" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Überprüfen Sie die Logs:" -ForegroundColor White
Write-Host "   docker logs valeo-neuro-erp-backend" -ForegroundColor Gray
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY-RUN] Keine Änderungen vorgenommen." -ForegroundColor $Yellow
}

Write-Host "Fertig!" -ForegroundColor $Green
