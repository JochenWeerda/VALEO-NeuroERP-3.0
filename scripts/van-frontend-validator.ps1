# ===================================================
# VAN-Modus Frontend-Validator
# ===================================================
# Dieses Skript prüft die Frontend-Entwicklungsumgebung
# auf Compliance mit den definierten VAN-Modus-Standards
# und korrigiert Probleme automatisch.
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
$tsConfigPath = Join-Path $frontendDir "tsconfig.json"

# Banner ausgeben
Write-Host ""
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host "  VAN-Modus Frontend-Validator - VALEO NeuroERP" -ForegroundColor Cyan
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

# 1. Verzeichnisstruktur-Validierung
Write-Info "1. Prüfe Verzeichnisstruktur..."

# Prüfe ob Frontend-Verzeichnis existiert
$frontendDirExists = Test-Path $frontendDir
Register-Check -Result $frontendDirExists -Name "Frontend-Verzeichnis existiert"

if (-not $frontendDirExists) {
    Write-Error "Kritischer Fehler: Frontend-Verzeichnis nicht gefunden!"
    Write-Info "Erstelle Frontend-Verzeichnis..."
    New-Item -ItemType Directory -Path $frontendDir | Out-Null
    Register-Check -Result $true -Name "Frontend-Verzeichnis erstellt" -Corrected $true
}

# Prüfe ob src-Verzeichnis existiert
$srcDirPath = Join-Path $frontendDir "src"
$srcDirExists = Test-Path $srcDirPath
Register-Check -Result $srcDirExists -Name "src-Verzeichnis existiert"

if (-not $srcDirExists) {
    Write-Info "Erstelle src-Verzeichnis..."
    New-Item -ItemType Directory -Path $srcDirPath | Out-Null
    Register-Check -Result $true -Name "src-Verzeichnis erstellt" -Corrected $true
}

# 2. Konfigurationsdateien-Prüfung
Write-Info "2. Prüfe Konfigurationsdateien..."

# Prüfe package.json
$packageJsonExists = Test-Path $packageJsonPath
Register-Check -Result $packageJsonExists -Name "package.json existiert"

if (-not $packageJsonExists) {
    Write-Info "Erstelle standard package.json..."
    
    $packageJsonContent = @{
        name = "valeo-neuroerp-frontend"
        description = "Frontend für das VALEO NeuroERP-System"
        version = "1.2.0"
        private = $true
        scripts = @{
            start = "vite"
            dev = "vite"
            build = "vite build"
            preview = "vite preview"
            lint = "eslint src --ext .js,.jsx,.ts,.tsx"
        }
        dependencies = @{
            "@emotion/react" = "^11.11.0"
            "@emotion/styled" = "^11.11.0"
            "@mui/icons-material" = "^5.11.16"
            "@mui/lab" = "^5.0.0-alpha.129"
            "@mui/material" = "^5.13.1"
            "@mui/x-data-grid" = "^6.4.0"
            "@mui/x-date-pickers" = "^6.4.0"
            "axios" = "^1.4.0"
            "chart.js" = "^4.3.0"
            "react" = "^18.2.0"
            "react-chartjs-2" = "^5.2.0"
            "react-dom" = "^18.2.0"
            "react-router-dom" = "^6.11.1"
        }
        devDependencies = @{
            "@types/react" = "^18.2.6"
            "@types/react-dom" = "^18.2.4"
            "@vitejs/plugin-react" = "^4.0.0"
            "eslint" = "^8.40.0"
            "eslint-plugin-react" = "^7.32.2"
            "eslint-plugin-react-hooks" = "^4.6.0"
            "typescript" = "^5.0.4"
            "vite" = "^4.3.5"
        }
    }
    
    $packageJsonContent | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath -Encoding UTF8
    Register-Check -Result $true -Name "package.json erstellt" -Corrected $true
} else {
    # Prüfe, ob Skripte in package.json vorhanden sind
    $packageJsonContent = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
    $hasStartScript = $packageJsonContent.scripts -and ($packageJsonContent.scripts.PSObject.Properties.Name -contains "start")
    Register-Check -Result $hasStartScript -Name "Start-Skript in package.json definiert"
    
    if (-not $hasStartScript) {
        Write-Info "Füge Start-Skript zu package.json hinzu..."
        
        if (-not $packageJsonContent.scripts) {
            $packageJsonContent | Add-Member -NotePropertyName "scripts" -NotePropertyValue @{
                "start" = "vite"
                "dev" = "vite"
                "build" = "vite build"
                "preview" = "vite preview"
            }
        } else {
            $packageJsonContent.scripts | Add-Member -NotePropertyName "start" -NotePropertyValue "vite" -Force
            $packageJsonContent.scripts | Add-Member -NotePropertyName "dev" -NotePropertyValue "vite" -Force
            $packageJsonContent.scripts | Add-Member -NotePropertyName "build" -NotePropertyValue "vite build" -Force
            $packageJsonContent.scripts | Add-Member -NotePropertyName "preview" -NotePropertyValue "vite preview" -Force
        }
        
        $packageJsonContent | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
        Register-Check -Result $true -Name "Start-Skript hinzugefügt" -Corrected $true
    }
    
    # Prüfe ob TypeScript als Abhängigkeit vorhanden ist
    $hasTypeScriptDep = $packageJsonContent.devDependencies -and ($packageJsonContent.devDependencies.PSObject.Properties.Name -contains "typescript")
    Register-Check -Result $hasTypeScriptDep -Name "TypeScript in package.json definiert"
    
    if (-not $hasTypeScriptDep) {
        Write-Info "TypeScript als devDependency zu package.json hinzufügen..."
        
        if (-not $packageJsonContent.devDependencies) {
            $packageJsonContent | Add-Member -NotePropertyName "devDependencies" -NotePropertyValue @{
                "typescript" = "^5.0.4"
            }
        } else {
            $packageJsonContent.devDependencies | Add-Member -NotePropertyName "typescript" -NotePropertyValue "^5.0.4" -Force
        }
        
        $packageJsonContent | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
        Register-Check -Result $true -Name "TypeScript-Abhängigkeit hinzugefügt" -Corrected $true
    }
}

# Prüfe vite.config.js
$viteConfigExists = Test-Path $viteConfigPath
Register-Check -Result $viteConfigExists -Name "vite.config.js existiert"

if (-not $viteConfigExists) {
    Write-Info "Erstelle standard vite.config.js..."
    
    @"
/**
 * Vite-Konfiguration für das ERP-Frontend
 * 
 * Diese Konfiguration wurde nach den Frontend-Development-Setup-Mustern optimiert,
 * um eine konsistente Entwicklungsumgebung zu gewährleisten und typische Probleme zu vermeiden.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  
  // Verbesserte Alias-Konfiguration für Import-Pfade
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@services': path.resolve(__dirname, './src/services'),
      '@utils': path.resolve(__dirname, './src/utils'),
    }
  },
  
  // JSX/TSX-Konfiguration
  esbuild: {
    loader: { '.js': 'jsx', '.ts': 'tsx' },
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment'
  },
  
  // Server-Konfiguration
  server: {
    port: 5173,
    strictPort: false,
    open: true
  }
});
"@ | Out-File -FilePath $viteConfigPath -Encoding utf8
    
    Register-Check -Result $true -Name "vite.config.js erstellt" -Corrected $true
} else {
    # Prüfe, ob JSX-Konfiguration in vite.config.js vorhanden ist
    $viteConfigContent = Get-Content -Path $viteConfigPath -Raw
    $hasJsxConfig = $viteConfigContent -match "loader.*['""].js['""].*jsx"
    Register-Check -Result $hasJsxConfig -Name "JSX-Konfiguration in vite.config.js vorhanden"
    
    if (-not $hasJsxConfig) {
        Write-Warning "JSX-Konfiguration fehlt in vite.config.js - Versuche automatische Korrektur"
        
        # Versuche, die JSX-Konfiguration hinzuzufügen
        if ($viteConfigContent -match "export default defineConfig\(\{") {
            $newConfig = $viteConfigContent -replace "export default defineConfig\(\{", @"
export default defineConfig({
  
  // JSX/TSX-Konfiguration
  esbuild: {
    loader: { '.js': 'jsx', '.ts': 'tsx' },
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment'
  },
"@
            $newConfig | Set-Content -Path $viteConfigPath -Encoding utf8
            Register-Check -Result $true -Name "JSX-Konfiguration zu vite.config.js hinzugefügt" -Corrected $true
        } else {
            Write-Error "Konnte JSX-Konfiguration nicht automatisch hinzufügen"
            Write-Info "JSX-Konfiguration muss manuell hinzugefügt werden:"
            Write-Host "esbuild: {
  loader: { '.js': 'jsx', '.ts': 'tsx' },
  jsxFactory: 'React.createElement',
  jsxFragment: 'React.Fragment'
}" -ForegroundColor Yellow
        }
    }
}

# Prüfe tsconfig.json
$tsConfigExists = Test-Path $tsConfigPath
Register-Check -Result $tsConfigExists -Name "tsconfig.json existiert"

if (-not $tsConfigExists) {
    Write-Info "Erstelle standard tsconfig.json..."
    
    @"
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@pages/*": ["./src/pages/*"],
      "@services/*": ["./src/services/*"],
      "@utils/*": ["./src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"@ | Out-File -FilePath $tsConfigPath -Encoding utf8
    
    Register-Check -Result $true -Name "tsconfig.json erstellt" -Corrected $true
    
    # Erstelle auch tsconfig.node.json wenn nicht vorhanden
    $tsConfigNodePath = Join-Path $frontendDir "tsconfig.node.json"
    if (-not (Test-Path $tsConfigNodePath)) {
        @"
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
"@ | Out-File -FilePath $tsConfigNodePath -Encoding utf8
        
        Write-Info "tsconfig.node.json ebenfalls erstellt"
    }
}

# 3. Abhängigkeiten-Prüfung
Write-Info "3. Prüfe kritische Abhängigkeiten..."

# Wechsle in das Frontend-Verzeichnis
Push-Location $frontendDir

# Prüfe, ob node_modules existiert
$nodeModulesExists = Test-Path (Join-Path $frontendDir "node_modules")
Register-Check -Result $nodeModulesExists -Name "node_modules Verzeichnis existiert"

if (-not $nodeModulesExists) {
    Write-Warning "node_modules Verzeichnis fehlt - Abhängigkeiten müssen installiert werden"
    Write-Info "Versuche 'npm install' auszuführen..."
    
    try {
        # Versuche, die Abhängigkeiten zu installieren
        npm install
        $installSuccess = $?
        Register-Check -Result $installSuccess -Name "Abhängigkeiten installiert" -Corrected $true
    } catch {
        Write-Error "Fehler beim Installieren der Abhängigkeiten: $_"
        Write-Info "Führe 'npm install' im Frontend-Verzeichnis aus, um Abhängigkeiten zu installieren"
    }
}

# Prüfe TypeScript
if ($nodeModulesExists) {
    $typescriptExists = Test-Path (Join-Path $frontendDir "node_modules/typescript")
    Register-Check -Result $typescriptExists -Name "TypeScript ist installiert"
    
    if (-not $typescriptExists) {
        Write-Warning "TypeScript fehlt - Versuche TypeScript zu installieren..."
        
        try {
            # Versuche, TypeScript zu installieren
            npm install typescript --save-dev
            $installSuccess = $?
            Register-Check -Result $installSuccess -Name "TypeScript installiert" -Corrected $true
        } catch {
            Write-Error "Fehler beim Installieren von TypeScript: $_"
            Write-Info "Führe 'npm install typescript --save-dev' aus, um TypeScript zu installieren"
        }
    }
}

# 4. Portverfügbarkeit prüfen
Write-Info "4. Prüfe Portverfügbarkeit..."

$standardPorts = @(5173, 5174, 5000, 3000)
$availablePorts = @()

foreach ($port in $standardPorts) {
    $portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if (-not $portInUse) {
        $availablePorts += $port
    }
}

if ($availablePorts.Count -gt 0) {
    Register-Check -Result $true -Name "Verfügbare Ports gefunden: $($availablePorts -join ', ')"
} else {
    Write-Warning "Alle Standard-Ports sind belegt!"
    Register-Check -Result $false -Name "Verfügbare Ports"
    Write-Info "Alternative Ports (8080, 8081, 8082) können beim Start verwendet werden"
}

# Wechsle zurück zum ursprünglichen Verzeichnis
Pop-Location

# Zusammenfassung
Write-Host ""
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host "  VAN-Modus Validierungsbericht" -ForegroundColor Cyan
Write-Host " ======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Durchgeführte Prüfungen: $totalChecks" -ForegroundColor White
Write-Host " Bestanden:               $passedChecks" -ForegroundColor Green
Write-Host " Fehlgeschlagen:          $failedChecks" -ForegroundColor Red
Write-Host " Automatisch korrigiert:  $correctedChecks" -ForegroundColor Yellow
Write-Host ""

# Handlungsempfehlung
if ($failedChecks -eq 0) {
    Write-Success "Frontend-Umgebung entspricht den VAN-Modus-Standards."
    Write-Info "Zum Starten des Frontends folgende Befehle ausführen:"
    Write-Host ""
    Write-Host "  cd frontend" -ForegroundColor White
    Write-Host "  npm start" -ForegroundColor White
    Write-Host ""
    Write-Info "Oder verwenden Sie das Frontend-Starter-Skript:"
    Write-Host ""
    Write-Host "  ./scripts/start_frontend.ps1" -ForegroundColor White
    Write-Host ""
    
    if ($availablePorts.Count -gt 0) {
        Write-Info "Empfohlener Port für Frontend-Start: $($availablePorts[0])"
        Write-Host ""
    }
} else {
    Write-Warning "Frontend-Umgebung entspricht nicht vollständig den VAN-Modus-Standards."
    Write-Info "Bitte beheben Sie die verbleibenden Probleme oder verwenden Sie das Frontend-Starter-Skript:"
    Write-Host ""
    Write-Host "  ./scripts/start_frontend.ps1" -ForegroundColor White
    Write-Host ""
    Write-Info "Dieses Skript wird automatisch alle erforderlichen Korrekturen vornehmen."
}

# Bei Bedarf automatisch zum Frontend-Verzeichnis wechseln
if ($failedChecks -eq 0 -and $args -contains "-cd") {
    Write-Info "Wechsle zum Frontend-Verzeichnis..."
    Set-Location $frontendDir
} 