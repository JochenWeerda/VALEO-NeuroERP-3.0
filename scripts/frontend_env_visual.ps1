# ===================================================
# Frontend-Umgebung Visualisierung
# ===================================================
# Dieses Skript erstellt eine visuelle Darstellung der
# Frontend-Entwicklungsumgebung und zeigt Statusberichte
# ===================================================

# Farbige Ausgabe-Funktionen für bessere Lesbarkeit
function Write-ColorOutput {
    param (
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Success {
    param ([string]$Text)
    Write-ColorOutput $Text "Green"
}

function Write-Error {
    param ([string]$Text)
    Write-ColorOutput $Text "Red"
}

function Write-Warning {
    param ([string]$Text)
    Write-ColorOutput $Text "Yellow"
}

function Write-Info {
    param ([string]$Text)
    Write-ColorOutput $Text "Cyan"
}

# Definiere Pfade
$rootDir = Join-Path $PSScriptRoot ".."
$frontendDir = Join-Path $rootDir "frontend"
$packageJsonPath = Join-Path $frontendDir "package.json"
$viteConfigPath = Join-Path $frontendDir "vite.config.js"
$rootPackageJsonPath = Join-Path $rootDir "package.json"

# Banner ausgeben
Write-Host ""
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Umgebung Visualisierung - Folkerts Landhandel ERP" -ForegroundColor Cyan
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host ""

# Prüfe Verzeichnisstruktur
$directories = @(
    "frontend",
    "frontend\src",
    "frontend\public",
    "frontend\node_modules"
)

Write-Info "Frontend-Verzeichnisstruktur:"
Write-Host ""
Write-Host "ERP-Projekt Root" -ForegroundColor White
Write-Host "+-- frontend/" -ForegroundColor $(if (Test-Path (Join-Path $rootDir "frontend")) { "Green" } else { "Red" })
Write-Host "    +-- src/" -ForegroundColor $(if (Test-Path (Join-Path $frontendDir "src")) { "Green" } else { "Red" })
Write-Host "    +-- public/" -ForegroundColor $(if (Test-Path (Join-Path $frontendDir "public")) { "Green" } else { "Red" })
Write-Host "    +-- node_modules/" -ForegroundColor $(if (Test-Path (Join-Path $frontendDir "node_modules")) { "Green" } else { "Yellow" })
Write-Host "    +-- package.json" -ForegroundColor $(if (Test-Path $packageJsonPath) { "Green" } else { "Red" })
Write-Host "    +-- vite.config.js" -ForegroundColor $(if (Test-Path $viteConfigPath) { "Green" } else { "Red" })
Write-Host "+-- scripts/" -ForegroundColor $(if (Test-Path (Join-Path $rootDir "scripts")) { "Green" } else { "Yellow" })
Write-Host "    +-- van-frontend-validator.ps1" -ForegroundColor $(if (Test-Path (Join-Path $PSScriptRoot "van-frontend-validator.ps1")) { "Green" } else { "Yellow" })
Write-Host "    +-- start_frontend.ps1" -ForegroundColor $(if (Test-Path (Join-Path $PSScriptRoot "start_frontend.ps1")) { "Green" } else { "Yellow" })
Write-Host "    +-- cd_frontend.ps1" -ForegroundColor $(if (Test-Path (Join-Path $PSScriptRoot "cd_frontend.ps1")) { "Green" } else { "Yellow" })
Write-Host "+-- package.json (Root)" -ForegroundColor $(if (Test-Path $rootPackageJsonPath) { "Green" } else { "Yellow" })
Write-Host ""

# Anzeige der Abhängigkeiten (wenn package.json vorhanden)
if (Test-Path $packageJsonPath) {
    Write-Info "Frontend-Abhängigkeiten:"
    Write-Host ""
    
    try {
        $packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
        
        if ($packageJson.dependencies) {
            $criticalDeps = @("react", "react-dom", "typescript")
            
            $depCount = 0
            $packageJson.dependencies.PSObject.Properties | ForEach-Object {
                $depCount++
                $depName = $_.Name
                $depVersion = $_.Value
                
                $color = "White"
                if ($criticalDeps -contains $depName) {
                    $color = "Green"
                }
                
                Write-Host "  $depName" -ForegroundColor $color -NoNewline
                Write-Host ": $depVersion" -ForegroundColor "Gray"
                
                # Begrenze die Anzeige auf maximal 10 Abhängigkeiten
                if ($depCount -ge 10) {
                    $remainingCount = $packageJson.dependencies.PSObject.Properties.Count - 10
                    if ($remainingCount -gt 0) {
                        Write-Host "  ... und $remainingCount weitere Abhängigkeiten" -ForegroundColor "Gray"
                    }
                    break
                }
            }
        } else {
            Write-Warning "  Keine Abhängigkeiten gefunden."
        }
    } catch {
        Write-Error "  Fehler beim Lesen der package.json: $_"
    }
}

# Status der Frontend-Umgebung
Write-Host ""
Write-Info "Frontend-Umgebungsstatus:"

$status = @{
    "Verzeichnisstruktur" = if ((Test-Path $frontendDir) -and (Test-Path (Join-Path $frontendDir "src"))) { "OK" } else { "Fehlend" }
    "package.json" = if (Test-Path $packageJsonPath) { "OK" } else { "Fehlend" }
    "vite.config.js" = if (Test-Path $viteConfigPath) { "OK" } else { "Fehlend" }
    "node_modules" = if (Test-Path (Join-Path $frontendDir "node_modules")) { "OK" } else { "Nicht installiert" }
    "Root package.json" = if (Test-Path $rootPackageJsonPath) { "OK" } else { "Fehlend" }
    "PowerShell Skripte" = if ((Test-Path (Join-Path $PSScriptRoot "van-frontend-validator.ps1")) -and 
                             (Test-Path (Join-Path $PSScriptRoot "start_frontend.ps1"))) { "OK" } else { "Unvollständig" }
}

$statusTable = @()
foreach ($key in $status.Keys) {
    $color = if ($status[$key] -eq "OK") { "Green" } else { "Red" }
    Write-Host "  $($key)" -NoNewline
    Write-Host ": $($status[$key])" -ForegroundColor $color
}

# JSX-Konfigurationsstatus
Write-Host ""
Write-Info "JSX-Konfigurationsstatus:"

if (Test-Path $viteConfigPath) {
    $viteConfigContent = Get-Content -Path $viteConfigPath -Raw
    $hasJsxConfig = $viteConfigContent -match "loader.*['""].js['""].*jsx"
    
    if ($hasJsxConfig) {
        Write-Success "  JSX-Konfiguration: Korrekt eingerichtet"
    } else {
        Write-Error "  JSX-Konfiguration: Fehlt in vite.config.js"
        Write-Host "  Empfohlene Konfiguration für JSX:" -ForegroundColor "Yellow"
        Write-Host "  esbuild: {" -ForegroundColor "White"
        Write-Host "    loader: { '.js': 'jsx', '.ts': 'tsx' }," -ForegroundColor "White"
        Write-Host "    jsxFactory: 'React.createElement'," -ForegroundColor "White"
        Write-Host "    jsxFragment: 'React.Fragment'" -ForegroundColor "White"
        Write-Host "  }" -ForegroundColor "White"
    }
} else {
    Write-Error "  JSX-Konfiguration: vite.config.js fehlt"
}

# Port-Status
Write-Host ""
Write-Info "Port-Status für Frontend-Entwicklung:"

$standardPorts = @(5173, 5174, 3000, 5000)
$portsStatus = @()

foreach ($port in $standardPorts) {
    try {
        $portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        $status = if ($portInUse) { "Belegt" } else { "Verfügbar" }
        $color = if ($portInUse) { "Yellow" } else { "Green" }
        
        Write-Host "  Port $($port)" -NoNewline
        Write-Host ": $status" -ForegroundColor $color
        
        if ($portInUse) {
            try {
                $process = Get-Process -Id $portInUse.OwningProcess -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "    Verwendet von: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor "Gray"
                }
            } catch {
                # Ignoriere Fehler bei der Prozessabfrage
            }
        }
    } catch {
        Write-Host "  Port $($port): Status konnte nicht ermittelt werden" -ForegroundColor "Yellow"
    }
}

# Empfehlungen
Write-Host ""
Write-Info "Empfehlungen für die Frontend-Entwicklung:"

if (-not (Test-Path $frontendDir)) {
    Write-Host "  1. Erstellen Sie das Frontend-Verzeichnis mit: mkdir frontend" -ForegroundColor "Yellow"
}

if (-not (Test-Path $packageJsonPath) -and (Test-Path $frontendDir)) {
    Write-Host "  2. Initialisieren Sie ein neues Frontend-Projekt im frontend-Verzeichnis:" -ForegroundColor "Yellow"
    Write-Host "     cd frontend; npm init -y" -ForegroundColor "White"
}

if (-not (Test-Path $viteConfigPath) -and (Test-Path $frontendDir)) {
    Write-Host "  3. Installieren Sie Vite und erstellen Sie eine vite.config.js:" -ForegroundColor "Yellow"
    Write-Host "     cd frontend; npm install vite" -ForegroundColor "White"
}

if (Test-Path $viteConfigPath) {
    $viteConfigContent = Get-Content -Path $viteConfigPath -Raw
    $hasJsxConfig = $viteConfigContent -match "loader.*['""].js['""].*jsx"
    
    if (-not $hasJsxConfig) {
        Write-Host "  4. Fügen Sie JSX-Unterstützung in vite.config.js hinzu" -ForegroundColor "Yellow"
    }
}

Write-Host "  5. Führen Sie das Frontend-Validierungsskript aus:" -ForegroundColor "Yellow"
Write-Host "     ./scripts/van-frontend-validator.ps1" -ForegroundColor "White"
Write-Host "  6. Verwenden Sie das Start-Frontend-Skript für den Entwicklungsserver:" -ForegroundColor "Yellow"
Write-Host "     ./scripts/start_frontend.ps1" -ForegroundColor "White"
Write-Host ""

# Abschluss
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Umgebung Visualisierung - Abgeschlossen" -ForegroundColor Cyan
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host "" 