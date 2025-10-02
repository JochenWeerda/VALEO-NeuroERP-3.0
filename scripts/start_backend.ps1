$ErrorActionPreference = "Stop"

# Projektverzeichnis bestimmen
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $projectRoot "backend"

Write-Host "Starting backend server from $backendPath"

# In das Backend-Verzeichnis wechseln
try {
    Push-Location $backendPath
} catch {
    Write-Error "Konnte nicht in das Backend-Verzeichnis wechseln: $_"
    exit 1
}

# Python-Umgebungsvariablen setzen
$env:PYTHONPATH = $backendPath
$env:PYTHONDONTWRITEBYTECODE = 1

# Server mit spezifischen Einstellungen starten
try {
    Write-Host "Starting uvicorn server..."
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Error "Fehler beim Starten des Backend-Servers: $_"
    exit 1
} finally {
    Pop-Location
} 