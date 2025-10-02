# ===================================================
# VAN-Modus Backend-Validator
# ===================================================
# Dieses Skript prüft die Backend-Entwicklungsumgebung
# auf Compliance mit den definierten VAN-Modus-Standards
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
$backendDir = Join-Path $rootDir "backend"
$requirementsPath = Join-Path $backendDir "requirements.txt"

# Banner ausgeben
Write-Host ""
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host "  VAN-Modus Backend-Validator - VALEO NeuroERP" -ForegroundColor Cyan
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host ""

# Zusammenfassung der Prüfungen
$totalChecks = 0
$passedChecks = 0
$failedChecks = 0
$correctedChecks = 0

function Register-Check {
    param (
        [bool]$Result,
        [string]$Name,
        [bool]$Corrected = $false
    )
    
    $script:totalChecks++
    
    if ($Result) {
        $script:passedChecks++
        Write-Success "[OK] $Name"
    } else {
        $script:failedChecks++
        if ($Corrected) {
            $script:correctedChecks++
            Write-Warning "[!] $Name (Korrigiert)"
        } else {
            Write-Error "[X] $Name"
        }
    }
}

# 1. Python-Version prüfen
Write-Info "1. Prüfe Python-Version..."

try {
    $pythonVersion = python --version 2>&1
    $pythonVersionMatch = $pythonVersion -match 'Python 3\.(1[0-3]|[3-9])'
    Register-Check -Result $pythonVersionMatch -Name "Python Version 3.3+ installiert"
    
    if (-not $pythonVersionMatch) {
        Write-Error "Python 3.3 oder höher wird benötigt!"
        Write-Info "Bitte installieren Sie eine aktuelle Python-Version von python.org"
    }
} catch {
    Register-Check -Result $false -Name "Python installiert"
    Write-Error "Python ist nicht installiert oder nicht im PATH!"
    Write-Info "Bitte installieren Sie Python von python.org"
}

# 2. Backend-Verzeichnisstruktur prüfen
Write-Info "2. Prüfe Backend-Verzeichnisstruktur..."

# Prüfe Backend-Hauptverzeichnis
$backendDirExists = Test-Path $backendDir
Register-Check -Result $backendDirExists -Name "Backend-Verzeichnis existiert"

if (-not $backendDirExists) {
    Write-Info "Erstelle Backend-Verzeichnis..."
    New-Item -ItemType Directory -Path $backendDir | Out-Null
    Register-Check -Result $true -Name "Backend-Verzeichnis erstellt" -Corrected $true
}

# Prüfe requirements.txt
$requirementsExists = Test-Path $requirementsPath
Register-Check -Result $requirementsExists -Name "Backend requirements.txt existiert"

if (-not $requirementsExists) {
    Write-Info "Erstelle standard requirements.txt..."
    @"
fastapi==0.95.2
uvicorn==0.22.0
sqlalchemy==2.0.12
alembic==1.10.4
pydantic==1.10.7
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiohttp==3.8.4
prometheus-client==0.16.0
celery==5.2.7
redis==4.5.4
"@ | Out-File -FilePath $requirementsPath -Encoding utf8
    Register-Check -Result $true -Name "requirements.txt erstellt" -Corrected $true
}

# Ausgabe der Zusammenfassung
Write-Host ""
Write-Host "VAN-Modus Backend-Validierung abgeschlossen" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "Gesamtanzahl Prüfungen: $totalChecks" -ForegroundColor White
Write-Host "Erfolgreich: $passedChecks" -ForegroundColor Green
Write-Host "Fehlgeschlagen: $failedChecks" -ForegroundColor Red
Write-Host "Automatisch korrigiert: $correctedChecks" -ForegroundColor Yellow
Write-Host ""

if ($failedChecks -gt 0) {
    Write-Warning "Es wurden $failedChecks Probleme gefunden!"
    exit 1
} else {
    Write-Success "Alle Prüfungen erfolgreich!"
    exit 0
} 