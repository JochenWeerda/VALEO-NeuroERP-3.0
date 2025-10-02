# ===================================================
# Frontend-Setup Skript
# ===================================================
# Automatisiertes Setup der Frontend-Entwicklungsumgebung
# für das Folkerts Landhandel ERP-System
# ===================================================

# Lade Hilfsfunktionen
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\powershell_compatibility.ps1"

# Banner anzeigen
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Setup - Folkerts Landhandel ERP" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""

# Pfade definieren
$rootDir = Split-Path -Parent $scriptPath
$frontendDir = Join-Path $rootDir "frontend"
$packageJsonPath = Join-Path $frontendDir "package.json"
$viteConfigPath = Join-Path $frontendDir "vite.config.js"
$rootPackageJsonPath = Join-Path $rootDir "package.json"

# Überprüfe, ob das Frontend-Verzeichnis existiert
if (-not (Test-Path $frontendDir)) {
    Write-Warning "Frontend-Verzeichnis nicht gefunden. Erstelle es..."
    New-Item -ItemType Directory -Path $frontendDir | Out-Null
    Write-Success "Frontend-Verzeichnis erstellt: $frontendDir"
}

# Ins Frontend-Verzeichnis wechseln
Set-Location $frontendDir
Write-Info "Arbeitsverzeichnis: $frontendDir"

# Überprüfe, ob package.json existiert
if (-not (Test-Path $packageJsonPath)) {
    Write-Warning "package.json nicht gefunden. Initialisiere npm-Projekt..."
    Invoke-Expression "npm init -y"
    Write-Success "npm-Projekt initialisiert"
}

# Überprüfe und installiere notwendige Abhängigkeiten
Write-Info "Überprüfe Frontend-Abhängigkeiten..."

$dependencies = @(
    "react",
    "react-dom",
    "typescript",
    "vite"
)

$devDependencies = @(
    "@types/react",
    "@types/react-dom",
    "@vitejs/plugin-react"
)

# Prüfe, ob Abhängigkeiten installiert sind
$packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
$needsInstall = $false

# Erstelle Abhängigkeitsobjekte, falls sie nicht existieren
if (-not $packageJson.dependencies) {
    $packageJson | Add-Member -MemberType NoteProperty -Name "dependencies" -Value (New-Object PSObject)
}

if (-not $packageJson.devDependencies) {
    $packageJson | Add-Member -MemberType NoteProperty -Name "devDependencies" -Value (New-Object PSObject)
}

# Überprüfe und markiere fehlende Abhängigkeiten
foreach ($dep in $dependencies) {
    if (-not $packageJson.dependencies.$dep) {
        Write-Warning "Abhängigkeit fehlt: $dep"
        $needsInstall = $true
    }
}

foreach ($dep in $devDependencies) {
    if (-not $packageJson.devDependencies.$dep) {
        Write-Warning "Dev-Abhängigkeit fehlt: $dep"
        $needsInstall = $true
    }
}

# Installiere fehlende Abhängigkeiten
if ($needsInstall) {
    Write-Info "Installiere fehlende Abhängigkeiten..."
    Invoke-Expression "npm install $($dependencies -join ' ')"
    Invoke-Expression "npm install --save-dev $($devDependencies -join ' ')"
    Write-Success "Abhängigkeiten installiert"
} else {
    Write-Success "Alle Abhängigkeiten sind bereits installiert"
}

# Überprüfe und erstelle Skripte in package.json
Write-Info "Überprüfe npm-Skripte..."

$requiredScripts = @{
    "start" = "vite"
    "dev" = "vite"
    "build" = "vite build"
    "preview" = "vite preview"
}

$scriptsUpdated = $false

# Erstelle scripts-Objekt, falls es nicht existiert
if (-not $packageJson.scripts) {
    $packageJson | Add-Member -MemberType NoteProperty -Name "scripts" -Value (New-Object PSObject)
}

# Überprüfe und aktualisiere Skripte
foreach ($scriptName in $requiredScripts.Keys) {
    if (-not $packageJson.scripts.$scriptName -or $packageJson.scripts.$scriptName -ne $requiredScripts[$scriptName]) {
        $packageJson.scripts | Add-Member -MemberType NoteProperty -Name $scriptName -Value $requiredScripts[$scriptName] -Force
        $scriptsUpdated = $true
    }
}

# Speichere aktualisierte package.json
if ($scriptsUpdated) {
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
    Write-Success "npm-Skripte aktualisiert"
} else {
    Write-Success "Alle npm-Skripte sind korrekt konfiguriert"
}

# Erstelle oder aktualisiere vite.config.js
if (-not (Test-Path $viteConfigPath)) {
    Write-Warning "vite.config.js nicht gefunden. Erstelle Standard-Konfiguration..."
    
    $viteConfig = @"
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  esbuild: {
    loader: { '.js': 'jsx' },
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment'
  },
  server: {
    port: 3000,
    open: true
  }
});
"@

    Set-Content -Path $viteConfigPath -Value $viteConfig
    Write-Success "vite.config.js erstellt mit JSX-Unterstützung"
} else {
    # Überprüfe und aktualisiere JSX-Konfiguration
    Set-JSXConfiguration -ViteConfigPath $viteConfigPath
}

# Erstelle Root-Package.json, falls sie nicht existiert
if (-not (Test-Path $rootPackageJsonPath)) {
    Write-Info "Erstelle Root-Package.json als Proxy..."
    
    $rootPackageJson = @"
{
  "name": "folkerts-landhandel-erp",
  "version": "1.0.0",
  "description": "Folkerts Landhandel ERP-System (Root-Verzeichnis)",
  "private": true,
  "scripts": {
    "start": "cd frontend && npm start",
    "dev": "cd frontend && npm run dev",
    "build": "cd frontend && npm run build",
    "preview": "cd frontend && npm run preview",
    "frontend": "cd frontend && npm",
    "frontend:install": "cd frontend && npm install",
    "frontend:validate": "powershell -File ./scripts/van-frontend-validator.ps1",
    "frontend:start": "powershell -File ./scripts/start_frontend.ps1"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=7.0.0"
  },
  "workspaces": [
    "frontend"
  ],
  "author": "Folkerts Landhandel",
  "license": "UNLICENSED"
}
"@

    Set-Content -Path $rootPackageJsonPath -Value $rootPackageJson
    Write-Success "Root-Package.json erstellt als Proxy für Frontend-Befehle"
}

# Erstelle eine einfache index.html und index.js, falls sie nicht existieren
$indexHtmlPath = Join-Path $frontendDir "index.html"
$srcDir = Join-Path $frontendDir "src"
$indexJsPath = Join-Path $srcDir "index.js"

if (-not (Test-Path $srcDir)) {
    New-Item -ItemType Directory -Path $srcDir | Out-Null
    Write-Success "src-Verzeichnis erstellt"
}

if (-not (Test-Path $indexHtmlPath)) {
    Write-Info "Erstelle index.html..."
    
    $indexHtml = @"
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Folkerts Landhandel ERP</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/index.js"></script>
</body>
</html>
"@

    Set-Content -Path $indexHtmlPath -Value $indexHtml
    Write-Success "index.html erstellt"
}

if (-not (Test-Path $indexJsPath)) {
    Write-Info "Erstelle index.js..."
    
    $indexJs = @"
import React from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Folkerts Landhandel ERP</h1>
      <p>Die Frontend-Umgebung wurde erfolgreich eingerichtet!</p>
    </div>
  );
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"@

    Set-Content -Path $indexJsPath -Value $indexJs
    Write-Success "index.js erstellt"
}

# Erfolgsmeldung anzeigen
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Frontend-Setup abgeschlossen!" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Info "Die Frontend-Umgebung wurde erfolgreich eingerichtet."
Write-Info "Starten Sie den Entwicklungsserver mit:"
Write-Host "  cd $frontendDir" -ForegroundColor White
Write-Host "  npm start" -ForegroundColor White
Write-Host ""
Write-Info "Oder aus dem Root-Verzeichnis mit:"
Write-Host "  npm run start" -ForegroundColor White
Write-Host ""
Write-Info "Oder mit dem Start-Skript:"
Write-Host "  ./scripts/start_frontend.ps1" -ForegroundColor White
Write-Host "" 