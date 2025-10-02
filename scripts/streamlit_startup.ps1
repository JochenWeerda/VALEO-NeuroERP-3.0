# PowerShell-Script zum Starten des GENXAIS v1.5 Dashboards
# Datei: scripts/streamlit_startup.ps1

Write-Host "Starte GENXAIS v1.5 Dashboard..." -ForegroundColor Cyan

# Prüfe, ob Streamlit installiert ist
try {
    $streamlitVersion = python -c "import streamlit; print(streamlit.__version__)" 2>$null
    if (-not $streamlitVersion) {
        Write-Host "Streamlit ist nicht installiert. Installiere Streamlit..." -ForegroundColor Yellow
        pip install streamlit altair pandas matplotlib networkx
    } else {
        Write-Host "Streamlit Version $streamlitVersion gefunden." -ForegroundColor Green
    }
} catch {
    Write-Host "Fehler beim Prüfen der Streamlit-Installation. Installiere Streamlit..." -ForegroundColor Yellow
    pip install streamlit altair pandas matplotlib networkx
}

# Erstelle Datenverzeichnisse, falls sie nicht existieren
$dataDir = "data/dashboard"
$graphitiDir = "data/dashboard/graphiti"

if (-not (Test-Path $dataDir)) {
    Write-Host "Erstelle Datenverzeichnis: $dataDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

if (-not (Test-Path $graphitiDir)) {
    Write-Host "Erstelle Graphiti-Verzeichnis: $graphitiDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $graphitiDir -Force | Out-Null
}

# Starte das Dashboard
Write-Host "Starte das Dashboard in einem neuen Fenster..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m streamlit run scripts/enhanced_dashboard.py"

Write-Host "Dashboard gestartet. Öffne http://localhost:8501 im Browser." -ForegroundColor Cyan
Write-Host "Drücke STRG+C, um das Dashboard zu beenden." -ForegroundColor Yellow 