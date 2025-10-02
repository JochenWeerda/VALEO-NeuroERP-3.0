# ===================================================
# Frontend-Starter Skript
# ===================================================
# Startet den Frontend-Entwicklungsserver mit 
# verbesserter PowerShell-Kompatibilität
# ===================================================

# Lade Hilfsfunktionen
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\powershell_compatibility.ps1"

$ErrorActionPreference = "Stop"

# Projektverzeichnis bestimmen
$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $projectRoot "frontend"

Write-Host @"
=====================================================
 Frontend-Starter - VALEO NeuroERP
=====================================================
"@

Write-Host "Arbeitsverzeichnis: $frontendPath"

# In das Frontend-Verzeichnis wechseln
try {
    Push-Location $frontendPath
} catch {
    Write-Error "Konnte nicht in das Frontend-Verzeichnis wechseln: $_"
    exit 1
}

# Node-Version prüfen
$nodeVersion = node -v
Write-Host "Verwende Node Version: $nodeVersion"
$npmVersion = npm -v
Write-Host "Verwende npm Version: $npmVersion"

# Vite Config prüfen und korrigieren
$viteConfigPath = Join-Path $frontendPath "vite.config.js"
if (!(Test-Path $viteConfigPath)) {
    Write-Warning "vite.config.js nicht gefunden. Wird erstellt..."
    Copy-Item (Join-Path $PSScriptRoot "templates" "vite.config.template.js") $viteConfigPath
}

# JSX-Konfiguration prüfen
$viteContent = Get-Content $viteConfigPath -Raw
if ($viteContent -notmatch "jsxFactory") {
    Write-Warning "JSX-Konfiguration in vite.config.js fehlt oder ist fehlerhaft. Wird korrigiert..."
    $viteContent = $viteContent -replace "plugins: \[", @"
plugins: [
    react({
      babel: {
        plugins: [
          ['@babel/plugin-transform-react-jsx', { runtime: 'automatic' }]
        ]
      }
    })
"@
    $viteContent | Set-Content $viteConfigPath
    Write-Host "JSX-Konfiguration wurde zu vite.config.js hinzugefügt"
}

# Node-Module installieren falls nötig
if (!(Test-Path "node_modules")) {
    Write-Host "Node-Module werden installiert..."
    npm install --silent
}

# Vite-Dev-Server starten
try {
    Write-Host "Starte Vite-Dev-Server..."
    npm run dev -- --port 5173 --host 0.0.0.0
} catch {
    Write-Error "Fehler beim Starten des Frontend-Servers: $_"
    exit 1
} finally {
    Pop-Location
}

Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Server beendet" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting frontend server from $frontendPath"
Set-Location $frontendPath

# Installiere Dependencies falls nötig
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..."
    npm install --silent
}

# Ports prüfen und freigeben
$ports = @(3000..3010)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Port $port is in use, stopping process..."
        Stop-Process -Id (Get-Process -Id $process.OwningProcess).Id -Force
    }
}

# Development Server mit spezifischem Port starten
$env:PORT = 3000
try {
    npm run dev
} catch {
    Write-Host "Error starting frontend server: $_"
    exit 1
} 