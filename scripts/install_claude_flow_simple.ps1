# Einfaches PowerShell-Skript zur Installation von Claude Flow
# Ausführung: PowerShell als Administrator starten

Write-Host "=== Claude Flow Installation ===" -ForegroundColor Green

# Prüfe Administratorrechte
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "FEHLER: Administratorrechte erforderlich!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Administratorrechte bestätigt" -ForegroundColor Green

# Setze Execution Policy
Write-Host "Setze Execution Policy..." -ForegroundColor Yellow
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
Write-Host "✓ Execution Policy gesetzt" -ForegroundColor Green

# Prüfe Node.js
Write-Host "Prüfe Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "Node.js nicht gefunden. Installiere..." -ForegroundColor Yellow
    winget install OpenJS.NodeJS
    Write-Host "✓ Node.js installiert" -ForegroundColor Green
}

# Prüfe npm
Write-Host "Prüfe npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "✓ npm: $npmVersion" -ForegroundColor Green
}
catch {
    Write-Host "FEHLER: npm nicht verfügbar" -ForegroundColor Red
    exit 1
}

# Wechsle zum Projektverzeichnis
Set-Location "C:\Users\Jochen\VALEO-NeuroERP-2.0"
Write-Host "✓ Projektverzeichnis: $(Get-Location)" -ForegroundColor Green

# Erstelle Claude Flow Verzeichnis
if (-not (Test-Path "claude-flow-alpha")) {
    New-Item -ItemType Directory -Name "claude-flow-alpha" -Force
    Write-Host "✓ Claude Flow Verzeichnis erstellt" -ForegroundColor Green
}

Set-Location "claude-flow-alpha"

# Initialisiere npm Projekt
if (-not (Test-Path "package.json")) {
    Write-Host "Initialisiere npm Projekt..." -ForegroundColor Yellow
    npm init -y
    Write-Host "✓ npm Projekt initialisiert" -ForegroundColor Green
}

# Installiere Dependencies
Write-Host "Installiere Dependencies..." -ForegroundColor Yellow
$deps = @("express", "cors", "dotenv", "ws", "uuid", "axios")
foreach ($dep in $deps) {
    npm install $dep
    Write-Host "✓ $dep installiert" -ForegroundColor Green
}

# Installiere Dev Dependencies
Write-Host "Installiere Dev Dependencies..." -ForegroundColor Yellow
$devDeps = @("typescript", "ts-node", "nodemon", "@types/node", "@types/express")
foreach ($dep in $devDeps) {
    npm install --save-dev $dep
    Write-Host "✓ $dep (dev) installiert" -ForegroundColor Green
}

# Erstelle TypeScript Config
$tsConfig = '{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}'
$tsConfig | Out-File -FilePath "tsconfig.json" -Encoding UTF8
Write-Host "✓ TypeScript Config erstellt" -ForegroundColor Green

# Erstelle src Verzeichnis
New-Item -ItemType Directory -Name "src" -Force | Out-Null

# Erstelle index.ts
$indexTs = 'import express from "express";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
    res.json({ 
        message: "Claude Flow Server läuft",
        version: "1.0.0",
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, () => {
    console.log(`Claude Flow Server läuft auf Port ${PORT}`);
});'
$indexTs | Out-File -FilePath "src\index.ts" -Encoding UTF8
Write-Host "✓ index.ts erstellt" -ForegroundColor Green

# Erstelle .env
$envContent = "# Claude Flow Konfiguration
PORT=3000
ANTHROPIC_API_KEY=your_api_key_here
NODE_ENV=development"
$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✓ .env erstellt" -ForegroundColor Green

# Erstelle .gitignore
$gitignore = "node_modules/
dist/
.env
*.log"
$gitignore | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "✓ .gitignore erstellt" -ForegroundColor Green

# Aktualisiere package.json Scripts
$packageJson = Get-Content "package.json" | ConvertFrom-Json
$packageJson.scripts = @{
    "start" = "node dist/index.js"
    "dev" = "nodemon src/index.ts"
    "build" = "tsc"
    "test" = "echo 'No tests specified'"
}
$packageJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "package.json" -Encoding UTF8
Write-Host "✓ package.json Scripts aktualisiert" -ForegroundColor Green

# Baue Projekt
Write-Host "Baue Projekt..." -ForegroundColor Yellow
try {
    npm run build
    Write-Host "✓ Projekt gebaut" -ForegroundColor Green
}
catch {
    Write-Host "Warnung: Build fehlgeschlagen" -ForegroundColor Yellow
}

# Erstelle Startskripte
$startScript = '@echo off
echo Starte Claude Flow Server...
cd /d "%~dp0claude-flow-alpha"
npm start
pause'
$startScript | Out-File -FilePath "start_claude_flow.bat" -Encoding ASCII

$devScript = '@echo off
echo Starte Claude Flow Server (Development)...
cd /d "%~dp0claude-flow-alpha"
npm run dev
pause'
$devScript | Out-File -FilePath "start_claude_flow_dev.bat" -Encoding ASCII

Write-Host "✓ Startskripte erstellt" -ForegroundColor Green

Write-Host ""
Write-Host "=== Installation abgeschlossen! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Yellow
Write-Host "1. Bearbeiten Sie .env und tragen Sie Ihren API Key ein" -ForegroundColor White
Write-Host "2. Starten Sie mit: start_claude_flow.bat" -ForegroundColor White
Write-Host "3. Development: start_claude_flow_dev.bat" -ForegroundColor White
Write-Host ""
Write-Host "Server: http://localhost:3000" -ForegroundColor Cyan 