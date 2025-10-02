# ===================================================
# Frontend-Umgebungstest für Folkerts Landhandel ERP
# ===================================================
# Dieses Skript testet die Frontend-Entwicklungsumgebung
# auf häufige Probleme und bietet Lösungen an
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
Write-Host "  Frontend-Umgebungstest - Folkerts Landhandel ERP" -ForegroundColor Cyan
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host ""

# Testbereich für Frontend-Startprobleme
$testsFailed = 0
$testsPassed = 0
$testsTotal = 0

function Register-TestResult {
    param (
        [bool]$Result,
        [string]$TestName,
        [string]$FailureMessage = "",
        [string]$SuccessMessage = ""
    )
    
    $script:testsTotal++
    
    if ($Result) {
        $script:testsPassed++
        if ($SuccessMessage) {
            Write-Success "[✓] $TestName - $SuccessMessage"
        } else {
            Write-Success "[✓] $TestName"
        }
    } else {
        $script:testsFailed++
        if ($FailureMessage) {
            Write-Error "[✗] $TestName - $FailureMessage"
        } else {
            Write-Error "[✗] $TestName"
        }
    }
}

# Test 1: Verzeichnisstruktur
Write-Info "1. Teste Verzeichnisstruktur..."

$frontendDirExists = Test-Path $frontendDir
Register-TestResult -Result $frontendDirExists -TestName "Frontend-Verzeichnis existiert" `
    -FailureMessage "Das Frontend-Verzeichnis fehlt!" `
    -SuccessMessage "Frontend-Verzeichnis gefunden unter $frontendDir"

if (-not $frontendDirExists) {
    Write-Info "Lösung: Führen Sie folgenden Befehl aus, um das Frontend-Verzeichnis zu erstellen:"
    Write-Host "  mkdir frontend" -ForegroundColor White
}

# Test 2: Konfigurationsdateien
Write-Info "2. Teste Konfigurationsdateien..."

$packageJsonExists = Test-Path $packageJsonPath
Register-TestResult -Result $packageJsonExists -TestName "package.json existiert im Frontend-Verzeichnis" `
    -FailureMessage "package.json fehlt im Frontend-Verzeichnis" `
    -SuccessMessage "package.json gefunden"

if ($packageJsonExists) {
    # Überprüfe ob start-Skript in package.json definiert ist
    $packageJsonContent = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
    $hasStartScript = $packageJsonContent.scripts -and ($packageJsonContent.scripts.PSObject.Properties.Name -contains "start")
    Register-TestResult -Result $hasStartScript -TestName "Start-Skript in package.json definiert" `
        -FailureMessage "Das 'start'-Skript fehlt in package.json" `
        -SuccessMessage "Start-Skript korrekt konfiguriert"
    
    if (-not $hasStartScript) {
        Write-Info "Lösung: Führen Sie den VAN-Modus Validator aus, um die package.json zu korrigieren:"
        Write-Host "  ./scripts/van-frontend-validator.ps1" -ForegroundColor White
    }
}

$viteConfigExists = Test-Path $viteConfigPath
Register-TestResult -Result $viteConfigExists -TestName "vite.config.js existiert" `
    -FailureMessage "vite.config.js fehlt im Frontend-Verzeichnis" `
    -SuccessMessage "vite.config.js gefunden"

if ($viteConfigExists) {
    # Überprüfe ob JSX-Konfiguration in vite.config.js vorhanden ist
    $viteConfigContent = Get-Content -Path $viteConfigPath -Raw
    $hasJsxConfig = $viteConfigContent -match "loader.*['""].js['""].*jsx"
    Register-TestResult -Result $hasJsxConfig -TestName "JSX-Konfiguration in vite.config.js" `
        -FailureMessage "Die JSX-Konfiguration fehlt in vite.config.js" `
        -SuccessMessage "JSX-Konfiguration korrekt"
    
    if (-not $hasJsxConfig) {
        Write-Info "Lösung: Die vite.config.js muss eine JSX-Konfiguration enthalten. Führen Sie den VAN-Modus Validator aus:"
        Write-Host "  ./scripts/van-frontend-validator.ps1" -ForegroundColor White
        Write-Info "Oder fügen Sie manuell folgende Konfiguration in vite.config.js ein:"
        Write-Host "  esbuild: {
    loader: { '.js': 'jsx', '.ts': 'tsx' },
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment'
  }" -ForegroundColor White
    }
}

# Test 3: Root package.json für Proxy-Befehle
Write-Info "3. Teste Root-Verzeichnis-Konfiguration..."

$rootPackageJsonExists = Test-Path $rootPackageJsonPath
Register-TestResult -Result $rootPackageJsonExists -TestName "package.json im Root-Verzeichnis" `
    -FailureMessage "Es fehlt eine package.json im Root-Verzeichnis" `
    -SuccessMessage "package.json im Root-Verzeichnis gefunden"

if ($rootPackageJsonExists) {
    # Überprüfe ob Frontend-Skripte in Root package.json definiert sind
    $rootPackageJsonContent = Get-Content -Path $rootPackageJsonPath -Raw | ConvertFrom-Json
    $hasProxyScripts = $rootPackageJsonContent.scripts -and 
                      ($rootPackageJsonContent.scripts.PSObject.Properties.Name -contains "start" -or
                       $rootPackageJsonContent.scripts.PSObject.Properties.Name -contains "frontend:start")
    Register-TestResult -Result $hasProxyScripts -TestName "Proxy-Skripte in Root package.json" `
        -FailureMessage "Es fehlen Proxy-Skripte in der Root package.json" `
        -SuccessMessage "Proxy-Skripte korrekt konfiguriert"
    
    if (-not $hasProxyScripts) {
        Write-Info "Lösung: Fügen Sie Proxy-Skripte in die Root package.json ein, z.B.:"
        Write-Host '  "scripts": {
    "start": "cd frontend && npm start",
    "frontend:start": "powershell -File ./scripts/start_frontend.ps1"
  }' -ForegroundColor White
    }
}

# Test 4: PowerShell-Kompatibilität
Write-Info "4. Teste PowerShell-Kompatibilität..."

# Teste ob PowerShell-Version ausreichend ist
$psVersion = $PSVersionTable.PSVersion.Major
$psVersionOk = $psVersion -ge 5
Register-TestResult -Result $psVersionOk -TestName "PowerShell-Version kompatibel" `
    -FailureMessage "PowerShell-Version $psVersion ist zu niedrig" `
    -SuccessMessage "PowerShell-Version $psVersion ist ausreichend"

if (-not $psVersionOk) {
    Write-Info "Lösung: Aktualisieren Sie PowerShell auf Version 5.1 oder höher."
}

# Test 5: Portverfügbarkeit
Write-Info "5. Teste Portverfügbarkeit..."

$standardPorts = @(5173, 5174, 5000, 3000)
$availablePorts = @()

foreach ($port in $standardPorts) {
    try {
        $portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if (-not $portInUse) {
            $availablePorts += $port
        }
    } catch {
        # Port konnte nicht überprüft werden, nehmen wir an er ist verfügbar
        $availablePorts += $port
    }
}

$hasAvailablePort = $availablePorts.Count -gt 0
Register-TestResult -Result $hasAvailablePort -TestName "Portverfügbarkeit" `
    -FailureMessage "Alle Standard-Ports sind belegt" `
    -SuccessMessage "Verfügbare Ports: $($availablePorts -join ', ')"

if (-not $hasAvailablePort) {
    Write-Info "Lösung: Beenden Sie Anwendungen, die Ports belegen, oder verwenden Sie einen alternativen Port beim Start:"
    Write-Host "  npm start -- --port 8080" -ForegroundColor White
}

# Test 6: Node.js und npm
Write-Info "6. Teste Node.js und npm..."

# Prüfe, ob npm verfügbar ist
try {
    $npmVersion = npm --version
    $npmAvailable = $?
} catch {
    $npmAvailable = $false
}

Register-TestResult -Result $npmAvailable -TestName "npm verfügbar" `
    -FailureMessage "npm ist nicht verfügbar oder nicht im PATH" `
    -SuccessMessage "npm Version $npmVersion gefunden"

if (-not $npmAvailable) {
    Write-Info "Lösung: Installieren Sie Node.js und npm von https://nodejs.org/"
}

# Zusammenfassung
Write-Host ""
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Umgebungstest - Zusammenfassung" -ForegroundColor Cyan
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Durchgeführte Tests: $testsTotal" -ForegroundColor White
Write-Host " Bestanden:           $testsPassed" -ForegroundColor Green
Write-Host " Fehlgeschlagen:      $testsFailed" -ForegroundColor Red
Write-Host ""

# Empfehlungen
if ($testsFailed -gt 0) {
    Write-Warning "Es wurden Probleme in der Frontend-Entwicklungsumgebung gefunden."
    Write-Info "Empfehlung: Führen Sie den VAN-Modus Validator aus, um Probleme automatisch zu beheben:"
    Write-Host "  ./scripts/van-frontend-validator.ps1" -ForegroundColor White
    Write-Host ""
    Write-Info "Alternativ können Sie das Frontend-Starter-Skript verwenden, das viele Probleme automatisch korrigiert:"
    Write-Host "  ./scripts/start_frontend.ps1" -ForegroundColor White
} else {
    Write-Success "Ihre Frontend-Entwicklungsumgebung ist korrekt konfiguriert!"
    Write-Info "Sie können den Frontend-Entwicklungsserver jetzt starten mit:"
    Write-Host "  cd frontend; npm start" -ForegroundColor White
    Write-Host ""
    Write-Info "Oder verwenden Sie die Hilfsskripte:"
    Write-Host "  ./scripts/cd_frontend.ps1" -ForegroundColor White
    Write-Host "  ./scripts/start_frontend.ps1" -ForegroundColor White
}

# Tipps für den Umgang mit PowerShell
Write-Host ""
Write-Info "Tipps für die Arbeit mit PowerShell:"
Write-Host "  - Verwenden Sie ';' statt '&&' zur Verkettung von Befehlen" -ForegroundColor White
Write-Host "  - Verwenden Sie 'Set-Location' oder 'cd' zum Verzeichniswechsel" -ForegroundColor White
Write-Host "  - Verwenden Sie 'Get-ChildItem' oder 'dir' zum Anzeigen von Verzeichnisinhalten" -ForegroundColor White
Write-Host "  - Weitere Tipps finden Sie in der Datei: ./scripts/powershell_tips.md" -ForegroundColor White
Write-Host "" 