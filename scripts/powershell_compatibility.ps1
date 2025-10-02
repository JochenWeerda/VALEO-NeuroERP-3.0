# ===================================================
# PowerShell-Kompatibilitätsfunktionen
# ===================================================
# Hilfsfunktionen für bessere PowerShell-Kompatibilität
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

# PowerShell-kompatible Befehlsverkettung (anstelle von &&)
function Invoke-CommandSequence {
    param (
        [Parameter(Mandatory=$true)]
        [string[]]$Commands
    )
    
    foreach ($cmd in $Commands) {
        Write-Info "Führe aus: $cmd"
        try {
            Invoke-Expression $cmd
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Befehl fehlgeschlagen: $cmd (Exit-Code: $LASTEXITCODE)"
                return $false
            }
        } catch {
            Write-Error "Fehler beim Ausführen von: $cmd`n$($_.Exception.Message)"
            return $false
        }
    }
    return $true
}

# Überprüfe, ob ein Port verfügbar ist
function Test-PortAvailable {
    param (
        [Parameter(Mandatory=$true)]
        [int]$Port
    )
    
    try {
        $tcpConnection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($tcpConnection) {
            return $false
        }
        return $true
    } catch {
        # Wenn ein Fehler auftritt, gehen wir davon aus, dass der Port verfügbar ist
        return $true
    }
}

# Finde einen freien Port
function Find-FreePort {
    param (
        [int]$StartPort = 3000,
        [int]$EndPort = 9000
    )
    
    for ($port = $StartPort; $port -le $EndPort; $port++) {
        if (Test-PortAvailable -Port $port) {
            return $port
        }
    }
    
    Write-Error "Konnte keinen freien Port zwischen $StartPort und $EndPort finden."
    return $null
}

# Wechsle ins Frontend-Verzeichnis und überprüfe die Existenz
function Set-FrontendDirectory {
    param (
        [string]$RootDir = (Get-Location).Path
    )
    
    $frontendDir = Join-Path $RootDir "frontend"
    
    if (-not (Test-Path $frontendDir)) {
        Write-Warning "Frontend-Verzeichnis nicht gefunden: $frontendDir"
        $createDir = Read-Host "Möchten Sie das Verzeichnis erstellen? (j/n)"
        if ($createDir -eq "j") {
            New-Item -ItemType Directory -Path $frontendDir | Out-Null
            Write-Success "Frontend-Verzeichnis erstellt: $frontendDir"
        } else {
            Write-Error "Frontend-Verzeichnis existiert nicht. Abbruch."
            return $false
        }
    }
    
    Set-Location $frontendDir
    Write-Success "Arbeitsverzeichnis geändert zu: $frontendDir"
    return $true
}

# Überprüfe, ob ein Prozess an einem bestimmten Port läuft und beende ihn bei Bedarf
function Stop-ProcessOnPort {
    param (
        [Parameter(Mandatory=$true)]
        [int]$Port,
        [switch]$Force
    )
    
    $tcpConnection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if ($tcpConnection) {
        $process = Get-Process -Id $tcpConnection.OwningProcess -ErrorAction SilentlyContinue
        
        if ($process) {
            Write-Warning "Port $Port wird von Prozess $($process.ProcessName) (PID: $($process.Id)) verwendet."
            
            if ($Force) {
                $shouldStop = "j"
            } else {
                $shouldStop = Read-Host "Möchten Sie diesen Prozess beenden? (j/n)"
            }
            
            if ($shouldStop -eq "j") {
                Stop-Process -Id $process.Id -Force
                Write-Success "Prozess $($process.ProcessName) (PID: $($process.Id)) wurde beendet."
                return $true
            } else {
                Write-Info "Prozess wird nicht beendet. Port $Port bleibt belegt."
                return $false
            }
        }
    }
    
    Write-Info "Kein Prozess auf Port $Port gefunden."
    return $true
}

# Überprüfen, ob die JSX-Konfiguration korrekt ist
function Test-JSXConfiguration {
    param (
        [string]$ViteConfigPath
    )
    
    if (-not (Test-Path $ViteConfigPath)) {
        Write-Error "vite.config.js nicht gefunden: $ViteConfigPath"
        return $false
    }
    
    $configContent = Get-Content -Path $ViteConfigPath -Raw
    $hasJsxConfig = $configContent -match "loader.*['""].js['""].*jsx"
    
    if (-not $hasJsxConfig) {
        Write-Warning "JSX-Konfiguration fehlt in vite.config.js"
        return $false
    }
    
    Write-Success "JSX-Konfiguration ist korrekt"
    return $true
}

# Automatisch die JSX-Konfiguration korrigieren
function Set-JSXConfiguration {
    param (
        [string]$ViteConfigPath
    )
    
    if (-not (Test-Path $ViteConfigPath)) {
        Write-Error "vite.config.js nicht gefunden: $ViteConfigPath"
        return $false
    }
    
    $configContent = Get-Content -Path $ViteConfigPath -Raw
    $hasJsxConfig = $configContent -match "loader.*['""].js['""].*jsx"
    
    if (-not $hasJsxConfig) {
        Write-Warning "JSX-Konfiguration wird zu vite.config.js hinzugefügt"
        
        # Prüfen, ob eine esbuild-Konfiguration bereits existiert
        $hasEsbuildConfig = $configContent -match "esbuild\s*:"
        
        if ($hasEsbuildConfig) {
            # Füge die JSX-Loader-Konfiguration zur bestehenden esbuild-Konfiguration hinzu
            $configContent = $configContent -replace "(esbuild\s*:\s*\{)", "`$1`n    loader: { '.js': 'jsx' },"
        } else {
            # Füge eine neue esbuild-Konfiguration hinzu
            $configContent = $configContent -replace "(defineConfig\s*\(\s*\{)", "`$1`n  esbuild: {`n    loader: { '.js': 'jsx' }`n  },"
        }
        
        Set-Content -Path $ViteConfigPath -Value $configContent
        Write-Success "JSX-Konfiguration wurde zu vite.config.js hinzugefügt"
        return $true
    }
    
    Write-Success "JSX-Konfiguration ist bereits korrekt"
    return $true
}

# Verzeichniswechsel-Funktion mit Fehlerbehandlung
function Set-WorkingDirectory {
    param (
        [string]$Path
    )
    try {
        Push-Location $Path
        return $true
    } catch {
        Write-Error "Konnte nicht in das Verzeichnis wechseln: $Path"
        return $false
    }
}

# Umgebungsvariablen-Management
function Set-EnvVar {
    param (
        [string]$Name,
        [string]$Value
    )
    try {
        [System.Environment]::SetEnvironmentVariable($Name, $Value, [System.EnvironmentVariableTarget]::Process)
        return $true
    } catch {
        Write-Error "Fehler beim Setzen der Umgebungsvariable $Name"
        return $false
    }
} 