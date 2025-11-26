# PowerShell Script: CRM Migration 003 - Sales Fields
# Fuehrt die Migration fuer SALES-CRM-02 aus

param(
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [string]$DbHost = "localhost",
    [string]$DbPort = "5432",
    [string]$Database = "valeo_neuroerp",
    [string]$DbUser = "valeo_user",
    [string]$DbPassword = "valeo_password"
)

$ErrorActionPreference = "Stop"

Write-Host "CRM Migration 003: Sales Fields (SALES-CRM-02)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Migration-Script-Pfad
$migrationFile = Join-Path $PSScriptRoot "..\migrations\sql\crm\003_add_sales_fields_to_customers.sql"

if (-not (Test-Path $migrationFile)) {
    Write-Host "ERROR: Migration-Script nicht gefunden: $migrationFile" -ForegroundColor Red
    exit 1
}

Write-Host "Migration-Script: $migrationFile" -ForegroundColor Green

# SQL-Inhalt lesen
$sqlContent = Get-Content $migrationFile -Raw -Encoding UTF8

# Datenbankverbindung aufbauen
Write-Host "Verbindung zur Datenbank..." -ForegroundColor Yellow

if ($DatabaseUrl) {
    # DATABASE_URL verwenden
    $connectionString = $DatabaseUrl
    Write-Host "   Verwendet DATABASE_URL" -ForegroundColor Gray
} else {
    # Einzelne Parameter verwenden
    $connectionString = "postgresql://${DbUser}:${DbPassword}@${DbHost}:${DbPort}/${Database}"
    Write-Host "   Host: $DbHost" -ForegroundColor Gray
    Write-Host "   Database: $Database" -ForegroundColor Gray
}

try {
    # Pruefe ob psql verfuegbar ist
    $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
    if (-not $psqlPath) {
        Write-Host "ERROR: psql nicht gefunden. Bitte PostgreSQL Client installieren." -ForegroundColor Red
        Write-Host "   Oder verwenden Sie Docker: docker exec -i postgres-container psql -U $DbUser -d $Database" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "OK: psql gefunden" -ForegroundColor Green
    Write-Host ""
    Write-Host "Fuehre Migration aus..." -ForegroundColor Yellow
    Write-Host ""

    # Migration ausfuehren
    if ($DatabaseUrl) {
        $env:PGPASSWORD = ($DatabaseUrl -split '@')[0] -replace '.*:', ''
        $dbPart = ($DatabaseUrl -split '@')[1]
        $hostPart = ($dbPart -split '/')[0]
        $dbName = ($dbPart -split '/')[1] -replace '\?.*', ''
        
        if ($hostPart -match ':') {
            $host = ($hostPart -split ':')[0]
            $port = ($hostPart -split ':')[1]
        } else {
            $host = $hostPart
            $port = "5432"
        }
        
        $user = (($DatabaseUrl -split '://')[1] -split ':')[0]
        
        $sqlContent | & psql -h $host -p $port -U $user -d $dbName -f $migrationFile
    } else {
        $env:PGPASSWORD = $Password
        $env:PGPASSWORD = $DbPassword
        $sqlContent | & psql -h $DbHost -p $DbPort -U $DbUser -d $Database -f $migrationFile
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "OK: Migration erfolgreich abgeschlossen!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Hinzugefuegte Felder:" -ForegroundColor Cyan
        Write-Host "  - price_group (VARCHAR(50))" -ForegroundColor Gray
        Write-Host "  - tax_category (VARCHAR(50))" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Indizes erstellt:" -ForegroundColor Cyan
        Write-Host "  - idx_crm_customers_price_group" -ForegroundColor Gray
        Write-Host "  - idx_crm_customers_tax_category" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "ERROR: Migration fehlgeschlagen (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host ""
    Write-Host "ERROR: Fehler bei Migration: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Manuell ausfuehren:" -ForegroundColor Yellow
    Write-Host "   psql -h $DbHost -p $DbPort -U $DbUser -d $Database -f $migrationFile" -ForegroundColor Gray
    exit 1
} finally {
    # PGPASSWORD zuruecksetzen
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Migration 003 abgeschlossen!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
