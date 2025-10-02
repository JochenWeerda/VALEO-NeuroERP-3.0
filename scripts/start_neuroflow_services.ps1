# =====================================================
# VALEO NeuroERP - NeuroFlow Services Start Script
# =====================================================
# PowerShell Script für automatische Service-Verwaltung
# Erstellt: 2025-07-23

Write-Host "🧠 VALEO NeuroERP - NeuroFlow Services Start Script" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

# Funktion für Service-Status-Check
function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$Url,
        [string]$Port
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $ServiceName läuft auf Port $Port" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "❌ $ServiceName nicht erreichbar auf Port $Port" -ForegroundColor Red
        return $false
    }
}

# Funktion für Docker-Container-Status
function Test-DockerContainer {
    param(
        [string]$ContainerName
    )
    
    try {
        $container = docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}"
        if ($container -match $ContainerName) {
            Write-Host "✅ Docker Container $ContainerName läuft" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Docker Container $ContainerName nicht gefunden" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Docker nicht verfügbar" -ForegroundColor Red
        return $false
    }
}

# Hauptverzeichnis setzen
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "📁 Projektverzeichnis: $ProjectRoot" -ForegroundColor Yellow

# =====================================================
# 1. DOCKER SERVICES STARTEN
# =====================================================

Write-Host "`n🐳 Starte Docker Services..." -ForegroundColor Magenta

# PostgreSQL Container starten
Write-Host "📊 Starte PostgreSQL..." -ForegroundColor Yellow
try {
    docker run -d --name valeo-postgres `
        -e POSTGRES_DB=valeo_neuroerp `
        -e POSTGRES_USER=valeo_user `
        -e POSTGRES_PASSWORD=valeo_password `
        -p 5432:5432 `
        postgres:15
    Write-Host "✅ PostgreSQL gestartet" -ForegroundColor Green
} catch {
    Write-Host "⚠️ PostgreSQL bereits läuft oder Fehler beim Starten" -ForegroundColor Yellow
}

# Redis Container starten
Write-Host "🔴 Starte Redis..." -ForegroundColor Yellow
try {
    docker run -d --name valeo-redis `
        -p 6379:6379 `
        redis:7-alpine
    Write-Host "✅ Redis gestartet" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Redis bereits läuft oder Fehler beim Starten" -ForegroundColor Yellow
}

# n8n Container starten
Write-Host "⚡ Starte n8n Workflow Automation..." -ForegroundColor Yellow
try {
    docker run -d --name valeo-n8n `
        -e N8N_BASIC_AUTH_ACTIVE=true `
        -e N8N_BASIC_AUTH_USER=admin `
        -e N8N_BASIC_AUTH_PASSWORD=admin123 `
        -e N8N_HOST=localhost `
        -e N8N_PORT=5678 `
        -e N8N_PROTOCOL=http `
        -e N8N_USER_MANAGEMENT_DISABLED=true `
        -e N8N_DIAGNOSTICS_ENABLED=false `
        -e N8N_METRICS=false `
        -e N8N_LOG_LEVEL=info `
        -e N8N_DEFAULT_LOCALE=de `
        -p 5678:5678 `
        n8nio/n8n:latest
    Write-Host "✅ n8n gestartet" -ForegroundColor Green
} catch {
    Write-Host "⚠️ n8n bereits läuft oder Fehler beim Starten" -ForegroundColor Yellow
}

# Warten für Container-Start
Write-Host "⏳ Warte auf Container-Start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# =====================================================
# 2. BACKEND SERVICES STARTEN
# =====================================================

Write-Host "`n🔧 Starte Backend Services..." -ForegroundColor Magenta

# Autocomplete API starten
Write-Host "🔍 Starte Autocomplete API (Port 8003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\backend'; python -m uvicorn api.autocomplete:app --host 0.0.0.0 --port 8003 --reload" -WindowStyle Minimized

# Charge Management API starten
Write-Host "📦 Starte Charge Management API (Port 8002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\backend'; python -m uvicorn api.charge_management:app --host 0.0.0.0 --port 8002 --reload" -WindowStyle Minimized

# Haupt-API starten (falls vorhanden)
Write-Host "🌐 Starte Haupt-API (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\backend'; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Minimized

# Warten für Backend-Start
Write-Host "⏳ Warte auf Backend-Start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# =====================================================
# 3. FRONTEND STARTEN
# =====================================================

Write-Host "`n🎨 Starte Frontend..." -ForegroundColor Magenta

Write-Host "⚛️ Starte React Frontend (Port 3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\frontend'; npm run dev" -WindowStyle Minimized

# Warten für Frontend-Start
Write-Host "⏳ Warte auf Frontend-Start..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# =====================================================
# 4. SERVICE HEALTH CHECKS
# =====================================================

Write-Host "`n🔍 Führe Service Health Checks durch..." -ForegroundColor Magenta

# Docker Container Status
Write-Host "`n🐳 Docker Container Status:" -ForegroundColor Cyan
Test-DockerContainer "valeo-postgres"
Test-DockerContainer "valeo-redis"
Test-DockerContainer "valeo-n8n"

# Backend API Status
Write-Host "`n🔧 Backend API Status:" -ForegroundColor Cyan
Test-ServiceHealth "Autocomplete API" "http://localhost:8003/health" "8003"
Test-ServiceHealth "Charge Management API" "http://localhost:8002/health" "8002"
Test-ServiceHealth "Haupt-API" "http://localhost:8000/health" "8000"

# Frontend Status
Write-Host "`n🎨 Frontend Status:" -ForegroundColor Cyan
Test-ServiceHealth "React Frontend" "http://localhost:3000" "3000"

# n8n Status
Write-Host "`n⚡ n8n Workflow Status:" -ForegroundColor Cyan
Test-ServiceHealth "n8n Workflow" "http://localhost:5678" "5678"

# =====================================================
# 5. ZUSAMMENFASSUNG
# =====================================================

Write-Host "`n📊 NeuroFlow Services Zusammenfassung:" -ForegroundColor Magenta
Write-Host "=====================================================" -ForegroundColor Magenta

Write-Host "`n🌐 Zugriff auf Services:" -ForegroundColor Yellow
Write-Host "• Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "• n8n Workflows: http://localhost:5678 (admin/admin123)" -ForegroundColor White
Write-Host "• Autocomplete API: http://localhost:8003" -ForegroundColor White
Write-Host "• Charge Management API: http://localhost:8002" -ForegroundColor White
Write-Host "• Haupt-API: http://localhost:8000" -ForegroundColor White

Write-Host "`n📁 Projektstruktur:" -ForegroundColor Yellow
Write-Host "• Frontend: $ProjectRoot\frontend" -ForegroundColor White
Write-Host "• Backend: $ProjectRoot\backend" -ForegroundColor White
Write-Host "• Database: $ProjectRoot\database" -ForegroundColor White
Write-Host "• Scripts: $ProjectRoot\scripts" -ForegroundColor White

Write-Host "`n✅ Alle NeuroFlow Services gestartet!" -ForegroundColor Green
Write-Host "🚀 VALEO NeuroERP ist bereit für die Entwicklung!" -ForegroundColor Green

# Script beenden
Write-Host "`n💡 Tipp: Verwende 'Get-Process | Where-Object {$_.ProcessName -eq 'python'}' um laufende Python-Prozesse zu sehen" -ForegroundColor Cyan
Write-Host "💡 Tipp: Verwende 'docker ps' um laufende Container zu sehen" -ForegroundColor Cyan

Read-Host "`nDrücke Enter um das Script zu beenden..." 