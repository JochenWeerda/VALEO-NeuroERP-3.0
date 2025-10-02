# ===================================================
# Frontend-Verzeichniswechsel Skript
# ===================================================
# Wechselt ins Frontend-Verzeichnis und zeigt 
# hilfreiche Befehle an
# ===================================================

# Lade Hilfsfunktionen
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\powershell_compatibility.ps1"

# Banner anzeigen
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Verzeichniswechsel - Folkerts Landhandel ERP" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""

# Pfade definieren
$rootDir = Split-Path -Parent $scriptPath
$frontendDir = Join-Path $rootDir "frontend"
$packageJsonPath = Join-Path $frontendDir "package.json"

# Überprüfe, ob Frontend-Verzeichnis existiert
if (-not (Test-Path $frontendDir)) {
    Write-Warning "Frontend-Verzeichnis nicht gefunden: $frontendDir"
    $createDir = Read-Host "Möchten Sie das Verzeichnis erstellen? (j/n)"
    
    if ($createDir -eq "j") {
        New-Item -ItemType Directory -Path $frontendDir | Out-Null
        Write-Success "Frontend-Verzeichnis erstellt: $frontendDir"
    } else {
        Write-Error "Frontend-Verzeichnis existiert nicht. Abbruch."
        exit 1
    }
}

# Ins Frontend-Verzeichnis wechseln
Set-Location $frontendDir
Write-Success "Arbeitsverzeichnis geändert zu: $frontendDir"

# Überprüfe, ob package.json existiert
$hasPackageJson = Test-Path $packageJsonPath
if ($hasPackageJson) {
    Write-Success "Frontend-Projekt gefunden (package.json vorhanden)"
    
    # Zeige verfügbare Skripte in package.json
    $packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
    if ($packageJson.scripts) {
        Write-Info "Verfügbare npm-Skripte:"
        $packageJson.scripts.PSObject.Properties | ForEach-Object {
            Write-Host "  npm run $($_.Name)" -ForegroundColor White
        }
    }
} else {
    Write-Warning "package.json nicht gefunden. Möglicherweise ist das Frontend-Projekt nicht initialisiert."
    Write-Info "Führen Sie folgende Befehle aus, um das Frontend-Projekt zu initialisieren:"
    Write-Host "  npm init -y" -ForegroundColor White
    Write-Host "  npm install react react-dom vite @vitejs/plugin-react" -ForegroundColor White
    Write-Host ""
    Write-Info "Oder verwenden Sie das Setup-Skript zur automatischen Einrichtung:"
    Write-Host "  ../scripts/setup_frontend.ps1" -ForegroundColor White
}

# Zeige verfügbare PowerShell-Skripte
Write-Host ""
Write-Info "Verfügbare PowerShell-Skripte:"
Write-Host "  ../scripts/setup_frontend.ps1     - Richtet die Frontend-Umgebung ein" -ForegroundColor White
Write-Host "  ../scripts/start_frontend.ps1     - Startet den Entwicklungsserver" -ForegroundColor White
Write-Host "  ../scripts/van-frontend-validator.ps1 - Validiert die Frontend-Umgebung" -ForegroundColor White
Write-Host ""

# Zeige PowerShell-Hinweise für die Frontend-Entwicklung
Write-Info "PowerShell-Tipps für die Frontend-Entwicklung:"
Write-Host "  - Verwenden Sie ';' anstatt '&&' für Befehlsverkettung in PowerShell" -ForegroundColor White
Write-Host "  - Beispiel: cd frontend; npm start" -ForegroundColor White
Write-Host "  - Setzen Sie Umgebungsvariablen mit `$env:VAR = 'Wert'" -ForegroundColor White
Write-Host "  - Beispiel: `$env:PORT = 3000; npm start" -ForegroundColor White
Write-Host ""

# Zeige typische npm-Befehle
Write-Info "Typische npm-Befehle:"
Write-Host "  npm start            - Startet den Entwicklungsserver" -ForegroundColor White
Write-Host "  npm run build        - Erstellt die Produktions-Build" -ForegroundColor White
Write-Host "  npm install <paket>  - Installiert ein npm-Paket" -ForegroundColor White
Write-Host "  npm list             - Zeigt installierte Pakete an" -ForegroundColor White
Write-Host ""

# Ermutigung und Abschluss
Write-Success "Sie sind bereit für die Frontend-Entwicklung!"
Write-Host "" 