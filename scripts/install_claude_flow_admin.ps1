# PowerShell-Skript zur Installation von Claude Flow mit Administratorrechten
# Ausführung: PowerShell als Administrator starten und dieses Skript ausführen

param(
    [switch]$Force = $false
)

# Prüfe Administratorrechte
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Hauptfunktion
function Install-ClaudeFlow {
    Write-Host "=== Claude Flow Installation mit Administratorrechten ===" -ForegroundColor Green
    Write-Host ""

    # Prüfe Administratorrechte
    if (-not (Test-Administrator)) {
        Write-Host "FEHLER: Dieses Skript muss mit Administratorrechten ausgeführt werden!" -ForegroundColor Red
        Write-Host "Bitte PowerShell als Administrator starten und das Skript erneut ausführen." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "✓ Administratorrechte bestätigt" -ForegroundColor Green

    # Setze Execution Policy
    Write-Host "Setze PowerShell Execution Policy..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "✓ Execution Policy gesetzt" -ForegroundColor Green
    }
    catch {
        Write-Host "Warnung: Execution Policy konnte nicht gesetzt werden: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # Prüfe Node.js Installation
    Write-Host "Prüfe Node.js Installation..." -ForegroundColor Yellow
    try {
        $nodeVersion = node --version
        Write-Host "✓ Node.js gefunden: $nodeVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "Node.js nicht gefunden. Installiere Node.js..." -ForegroundColor Yellow
        
        # Installiere Node.js über winget
        try {
            winget install OpenJS.NodeJS
            Write-Host "✓ Node.js installiert" -ForegroundColor Green
            
            # Aktualisiere PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
            
            # Prüfe Installation erneut
            $nodeVersion = node --version
            Write-Host "✓ Node.js Version: $nodeVersion" -ForegroundColor Green
        }
        catch {
            Write-Host "FEHLER: Node.js Installation fehlgeschlagen" -ForegroundColor Red
            Write-Host "Bitte installieren Sie Node.js manuell von https://nodejs.org/" -ForegroundColor Yellow
            exit 1
        }
    }

    # Prüfe npm Installation
    Write-Host "Prüfe npm Installation..." -ForegroundColor Yellow
    try {
        $npmVersion = npm --version
        Write-Host "✓ npm gefunden: $npmVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "FEHLER: npm nicht gefunden" -ForegroundColor Red
        exit 1
    }

    # Wechsle zum Projektverzeichnis
    $projectPath = "C:\Users\Jochen\VALEO-NeuroERP-2.0"
    if (Test-Path $projectPath) {
        Set-Location $projectPath
        Write-Host "✓ Zum Projektverzeichnis gewechselt: $projectPath" -ForegroundColor Green
    }
    else {
        Write-Host "FEHLER: Projektverzeichnis nicht gefunden: $projectPath" -ForegroundColor Red
        exit 1
    }

    # Prüfe ob Claude Flow bereits installiert ist
    if (Test-Path "claude-flow-alpha") {
        Write-Host "Claude Flow Verzeichnis gefunden. Prüfe Installation..." -ForegroundColor Yellow
        
        Set-Location "claude-flow-alpha"
        
        # Prüfe package.json
        if (Test-Path "package.json") {
            Write-Host "✓ package.json gefunden" -ForegroundColor Green
            
            # Installiere Dependencies
            Write-Host "Installiere Dependencies..." -ForegroundColor Yellow
            try {
                npm install
                Write-Host "✓ Dependencies installiert" -ForegroundColor Green
            }
            catch {
                Write-Host "FEHLER: Dependencies Installation fehlgeschlagen" -ForegroundColor Red
                Write-Host $_.Exception.Message -ForegroundColor Red
                exit 1
            }
        }
        else {
            Write-Host "package.json nicht gefunden. Claude Flow Installation unvollständig." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "Claude Flow Verzeichnis nicht gefunden. Erstelle Installation..." -ForegroundColor Yellow
        
        # Erstelle Claude Flow Verzeichnis
        New-Item -ItemType Directory -Name "claude-flow-alpha" -Force | Out-Null
        Set-Location "claude-flow-alpha"
        
        # Initialisiere npm Projekt
        Write-Host "Initialisiere npm Projekt..." -ForegroundColor Yellow
        try {
            npm init -y
            Write-Host "✓ npm Projekt initialisiert" -ForegroundColor Green
        }
        catch {
            Write-Host "FEHLER: npm Projekt Initialisierung fehlgeschlagen" -ForegroundColor Red
            exit 1
        }
    }

    # Installiere Claude Flow Dependencies
    Write-Host "Installiere Claude Flow Dependencies..." -ForegroundColor Yellow
    
    $dependencies = @(
        "@anthropic-ai/sdk",
        "express",
        "cors",
        "dotenv",
        "ws",
        "uuid",
        "axios",
        "node-fetch"
    )

    foreach ($dep in $dependencies) {
        try {
            Write-Host "Installiere $dep..." -ForegroundColor Yellow
            npm install $dep
            Write-Host "✓ $dep installiert" -ForegroundColor Green
        }
        catch {
            Write-Host "Warnung: Installation von $dep fehlgeschlagen: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    # Installiere Development Dependencies
    Write-Host "Installiere Development Dependencies..." -ForegroundColor Yellow
    
    $devDependencies = @(
        "@types/node",
        "@types/express",
        "@types/cors",
        "@types/ws",
        "@types/uuid",
        "typescript",
        "ts-node",
        "nodemon"
    )

    foreach ($dep in $devDependencies) {
        try {
            Write-Host "Installiere $dep (dev)..." -ForegroundColor Yellow
            npm install --save-dev $dep
            Write-Host "✓ $dep installiert" -ForegroundColor Green
        }
        catch {
            Write-Host "Warnung: Installation von $dep fehlgeschlagen: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    # Erstelle TypeScript Konfiguration
    Write-Host "Erstelle TypeScript Konfiguration..." -ForegroundColor Yellow
    $tsConfig = '{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}'

    $tsConfig | Out-File -FilePath "tsconfig.json" -Encoding UTF8
    Write-Host "✓ TypeScript Konfiguration erstellt" -ForegroundColor Green

    # Erstelle package.json Scripts
    Write-Host "Aktualisiere package.json Scripts..." -ForegroundColor Yellow
    
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    
    $packageJson.scripts = @{
        "start" = "node dist/index.js"
        "dev" = "nodemon src/index.ts"
        "build" = "tsc"
        "watch" = "tsc --watch"
        "test" = "echo 'Error: no test specified'"
    }
    
    $packageJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "package.json" -Encoding UTF8
    Write-Host "✓ package.json Scripts aktualisiert" -ForegroundColor Green

    # Erstelle src Verzeichnis und Basis-Dateien
    Write-Host "Erstelle Basis-Dateien..." -ForegroundColor Yellow
    
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
    console.log(`Server URL: http://localhost:${PORT}`);
});'

    $indexTs | Out-File -FilePath "src\index.ts" -Encoding UTF8
    Write-Host "✓ index.ts erstellt" -ForegroundColor Green

    # Erstelle .env Datei
    $envContent = "# Claude Flow Konfiguration
PORT=3000
ANTHROPIC_API_KEY=your_api_key_here
NODE_ENV=development"

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✓ .env Datei erstellt" -ForegroundColor Green

    # Erstelle .gitignore
    $gitignore = "node_modules/
dist/
.env
*.log
.DS_Store"

    $gitignore | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✓ .gitignore erstellt" -ForegroundColor Green

    # Baue das Projekt
    Write-Host "Baue das Projekt..." -ForegroundColor Yellow
    try {
        npm run build
        Write-Host "✓ Projekt erfolgreich gebaut" -ForegroundColor Green
    }
    catch {
        Write-Host "Warnung: Build fehlgeschlagen: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # Erstelle Startskript
    Write-Host "Erstelle Startskript..." -ForegroundColor Yellow
    
    $startScript = '@echo off
echo Starte Claude Flow Server...
cd /d "%~dp0claude-flow-alpha"
npm start
pause'

    $startScript | Out-File -FilePath "start_claude_flow.bat" -Encoding ASCII
    Write-Host "✓ Startskript erstellt: start_claude_flow.bat" -ForegroundColor Green

    # Erstelle Development Startskript
    $devStartScript = '@echo off
echo Starte Claude Flow Server im Development Mode...
cd /d "%~dp0claude-flow-alpha"
npm run dev
pause'

    $devStartScript | Out-File -FilePath "start_claude_flow_dev.bat" -Encoding ASCII
    Write-Host "✓ Development Startskript erstellt: start_claude_flow_dev.bat" -ForegroundColor Green

    Write-Host ""
    Write-Host "=== Installation abgeschlossen! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Nächste Schritte:" -ForegroundColor Yellow
    Write-Host "1. Bearbeiten Sie die .env Datei und tragen Sie Ihren Anthropic API Key ein" -ForegroundColor White
    Write-Host "2. Starten Sie den Server mit: start_claude_flow.bat" -ForegroundColor White
    Write-Host "3. Für Development: start_claude_flow_dev.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "Server wird auf http://localhost:3000 laufen" -ForegroundColor Cyan
}

# Führe Installation aus
Install-ClaudeFlow 