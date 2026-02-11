#!/usr/bin/env pwsh
#
# VALEO-NeuroERP - L3 Screenshot Automation Runner
# Wird vom Task Scheduler alle 5 Minuten aufgerufen
#

$ErrorActionPreference = "Stop"

# Log-Datei
$LogFile = "C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\screenshot-automation.log"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    Write-Host $LogMessage
}

Write-Log "🚀 L3-Screenshot-Automation gestartet"

# Wechsle ins Playwright-Verzeichnis
$PlaywrightDir = "C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\playwright-snap"
Set-Location $PlaywrightDir
Write-Log "📁 Verzeichnis: $PlaywrightDir"

# Prüfe ob Docker läuft
try {
    docker ps | Out-Null
    Write-Log "✅ Docker läuft"
} catch {
    Write-Log "❌ Docker läuft nicht - Abbruch"
    exit 1
}

# Prüfe ob Guacamole-Container läuft
$GuacContainer = docker ps --filter "name=l3-guacamole" --format "{{.Names}}"
if (-not $GuacContainer) {
    Write-Log "❌ Guacamole-Container läuft nicht - Abbruch"
    exit 1
}
Write-Log "✅ Guacamole-Container läuft: $GuacContainer"

# Umgebungsvariablen setzen
$env:GUAC_URL = "http://localhost:8090/guacamole"
$env:GUAC_USER = "guacadmin"
$env:GUAC_PASS = "GuacSecure2024!"  # ⚠️ ANPASSEN!
$env:CONNECTION_NAME = "L3-Windows-RDP"
$env:OUT_DIR = "C:/Users/Jochen/VALEO-NeuroERP-3.0/l3-migration-toolkit/screenshots"
$env:WAIT_SECONDS = "10"

Write-Log "📸 Erstelle Screenshot..."

# Screenshot erstellen
try {
    $output = npm run snap 2>&1
    Write-Log "✅ Screenshot erfolgreich erstellt"
    Write-Log $output
} catch {
    Write-Log "❌ Fehler beim Screenshot: $_"
    exit 1
}

# Statistik
$Screenshots = Get-ChildItem "$env:OUT_DIR\*.png"
$TotalSize = ($Screenshots | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Log "📊 Gesamt-Screenshots: $($Screenshots.Count) ($([math]::Round($TotalSize, 2)) MB)"

Write-Log "✅ Automation abgeschlossen`n"
exit 0


