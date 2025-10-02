# Redis-Installation und Konfiguration für Windows
#
# Dieses Skript lädt Redis für Windows herunter, extrahiert und konfiguriert es
# mit optimaler Persistenz- und Leistungskonfiguration.
#
# Verwendung: .\install_redis.ps1 [-RedisPort <Port>] [-ConfigOnly]

param (
    [int]$RedisPort = 6379,
    [switch]$ConfigOnly
)

# Konfiguration
$WORKSPACE_ROOT = "C:\AI_driven_ERP\AI_driven_ERP"
$REDIS_DIR = Join-Path $WORKSPACE_ROOT "redis"
$DOWNLOADS_DIR = Join-Path $WORKSPACE_ROOT "downloads"
$LOGS_DIR = Join-Path $WORKSPACE_ROOT "logs"
$REDIS_CONFIG = Join-Path $REDIS_DIR "redis.conf"
$REDIS_DATA_DIR = Join-Path $REDIS_DIR "data"

# URL für Redis für Windows
$REDIS_URL = "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip"
$REDIS_ZIP = Join-Path $DOWNLOADS_DIR "redis.zip"

# Funktion zum Schreiben von farbigen Nachrichten
function Write-ColorMessage {
    param (
        [string]$Message,
        [string]$ForegroundColor = "White"
    )
    
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Erstelle Verzeichnisse, falls sie nicht existieren
function Create-DirectoryIfNotExists {
    param (
        [string]$Path,
        [string]$Description
    )
    
    if (-not (Test-Path $Path)) {
        Write-ColorMessage "Erstelle $Description-Verzeichnis: $Path" -ForegroundColor Cyan
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

# Lade Redis herunter, falls erforderlich
function Download-Redis {
    if ($ConfigOnly) {
        if (-not (Test-Path $REDIS_DIR)) {
            Write-ColorMessage "FEHLER: Redis-Verzeichnis nicht gefunden: $REDIS_DIR" -ForegroundColor Red
            Write-ColorMessage "Bei Verwendung von -ConfigOnly muss Redis bereits installiert sein." -ForegroundColor Red
            return $false
        }
        return $true
    }
    
    if (-not (Test-Path $REDIS_DIR) -or -not (Test-Path (Join-Path $REDIS_DIR "redis-server.exe"))) {
        Create-DirectoryIfNotExists -Path $DOWNLOADS_DIR -Description "Downloads"
        
        if (-not (Test-Path $REDIS_ZIP)) {
            Write-ColorMessage "Lade Redis herunter..." -ForegroundColor Cyan
            try {
                [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
                Invoke-WebRequest -Uri $REDIS_URL -OutFile $REDIS_ZIP
                Write-ColorMessage "Redis erfolgreich heruntergeladen" -ForegroundColor Green
            } catch {
                Write-ColorMessage "FEHLER beim Herunterladen von Redis: $_" -ForegroundColor Red
                return $false
            }
        } else {
            Write-ColorMessage "Redis-ZIP bereits heruntergeladen" -ForegroundColor Yellow
        }
        
        # Extrahiere Redis
        Write-ColorMessage "Extrahiere Redis..." -ForegroundColor Cyan
        try {
            if (Test-Path $REDIS_DIR) {
                Remove-Item -Path $REDIS_DIR -Recurse -Force
            }
            Expand-Archive -Path $REDIS_ZIP -DestinationPath $REDIS_DIR
            Write-ColorMessage "Redis erfolgreich extrahiert" -ForegroundColor Green
        } catch {
            Write-ColorMessage "FEHLER beim Extrahieren von Redis: $_" -ForegroundColor Red
            return $false
        }
    } else {
        Write-ColorMessage "Redis ist bereits installiert" -ForegroundColor Yellow
    }
    
    return $true
}

# Erstelle optimierte Redis-Konfiguration
function Create-RedisConfig {
    Create-DirectoryIfNotExists -Path $REDIS_DATA_DIR -Description "Redis-Daten"
    
    Write-ColorMessage "Erstelle optimierte Redis-Konfiguration..." -ForegroundColor Cyan
    
    $config = @"
# Redis-Konfiguration für ERP-System
# Optimiert für Persistenz und Leistung

# Netzwerk
bind 127.0.0.1
port $RedisPort
timeout 0
tcp-keepalive 300

# Allgemein
daemonize no
pidfile redis_$RedisPort.pid
loglevel notice
logfile "$LOGS_DIR\redis.log"

# Persistenz
dir "$REDIS_DATA_DIR"
dbfilename dump.rdb

# RDB-Persistenz (regelmäßige Snapshots)
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes

# AOF-Persistenz (Operation-Log, höhere Datensicherheit)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Speicher-Management
maxmemory 1gb
maxmemory-policy volatile-lru
maxmemory-samples 5

# Leistungsoptimierungen
activerehashing yes
"@
    
    try {
        $config | Out-File -FilePath $REDIS_CONFIG -Encoding utf8
        Write-ColorMessage "Redis-Konfiguration erfolgreich erstellt: $REDIS_CONFIG" -ForegroundColor Green
        return $true
    } catch {
        Write-ColorMessage "FEHLER beim Erstellen der Redis-Konfiguration: $_" -ForegroundColor Red
        return $false
    }
}

# Erstelle Redis-Startskript
function Create-RedisStartScript {
    $startScript = Join-Path $REDIS_DIR "start_redis.ps1"
    
    $scriptContent = @"
# Start-Redis.ps1
#
# Dieses Skript startet Redis mit optimierter Konfiguration.
#
# Verwendung: .\start_redis.ps1

Set-Location "`$PSScriptRoot"
Write-Host "Starte Redis..." -ForegroundColor Cyan
Start-Process -FilePath "redis-server.exe" -ArgumentList "redis.conf" -NoNewWindow
Write-Host "Redis gestartet auf Port $RedisPort" -ForegroundColor Green
"@
    
    try {
        $scriptContent | Out-File -FilePath $startScript -Encoding utf8
        Write-ColorMessage "Redis-Startskript erfolgreich erstellt: $startScript" -ForegroundColor Green
        return $true
    } catch {
        Write-ColorMessage "FEHLER beim Erstellen des Redis-Startskripts: $_" -ForegroundColor Red
        return $false
    }
}

# Teste die Redis-Installation
function Test-Redis {
    $redisCliPath = Join-Path $REDIS_DIR "redis-cli.exe"
    
    if (-not (Test-Path $redisCliPath)) {
        Write-ColorMessage "WARNUNG: redis-cli.exe nicht gefunden, kann Redis-Verbindung nicht testen" -ForegroundColor Yellow
        return $true
    }
    
    Write-ColorMessage "Teste Redis-Verbindung..." -ForegroundColor Cyan
    
    # Prüfe, ob Redis bereits läuft
    $testResult = $null
    try {
        # Verwende PowerShell für den Test statt redis-cli
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("127.0.0.1", $RedisPort)
        $tcpClient.Close()
        Write-ColorMessage "Redis läuft bereits auf Port $RedisPort" -ForegroundColor Yellow
    } catch {
        # Redis läuft nicht, starte es
        Write-ColorMessage "Redis ist nicht aktiv, starte Redis..." -ForegroundColor Cyan
        
        try {
            $redisServerPath = Join-Path $REDIS_DIR "redis-server.exe"
            $redisConfigPath = Join-Path $REDIS_DIR "redis.conf"
            
            # Starte Redis im Hintergrund
            $process = Start-Process -FilePath $redisServerPath -ArgumentList $redisConfigPath -PassThru -WindowStyle Minimized
            Start-Sleep -Seconds 2
            
            # Teste die Verbindung erneut
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.Connect("127.0.0.1", $RedisPort)
            $tcpClient.Close()
            
            Write-ColorMessage "Redis erfolgreich gestartet und getestet" -ForegroundColor Green
            
            # Beende Redis wieder für den Test
            Stop-Process -Id $process.Id -Force
            Write-ColorMessage "Redis-Testinstanz beendet" -ForegroundColor Yellow
        } catch {
            Write-ColorMessage "FEHLER beim Testen der Redis-Verbindung: $_" -ForegroundColor Red
            return $false
        }
    }
    
    return $true
}

# Hauptprogramm
function Main {
    Write-ColorMessage "===== Redis-Installation und Konfiguration =====" -ForegroundColor Cyan
    
    # Erstelle Log-Verzeichnis
    Create-DirectoryIfNotExists -Path $LOGS_DIR -Description "Logs"
    
    # Lade Redis herunter und extrahiere es
    if (-not (Download-Redis)) {
        Write-ColorMessage "Installation abgebrochen aufgrund von Fehlern" -ForegroundColor Red
        return
    }
    
    # Erstelle optimierte Redis-Konfiguration
    if (-not (Create-RedisConfig)) {
        Write-ColorMessage "Konfiguration abgebrochen aufgrund von Fehlern" -ForegroundColor Red
        return
    }
    
    # Erstelle Redis-Startskript
    if (-not (Create-RedisStartScript)) {
        Write-ColorMessage "Erstellung des Startskripts fehlgeschlagen" -ForegroundColor Red
        return
    }
    
    # Teste die Redis-Installation
    if (-not (Test-Redis)) {
        Write-ColorMessage "Redis-Test fehlgeschlagen, aber Installation wurde abgeschlossen" -ForegroundColor Yellow
    }
    
    Write-ColorMessage "`nRedis-Installation und Konfiguration abgeschlossen!" -ForegroundColor Green
    Write-ColorMessage "Redis-Verzeichnis: $REDIS_DIR" -ForegroundColor White
    Write-ColorMessage "Konfigurationsdatei: $REDIS_CONFIG" -ForegroundColor White
    Write-ColorMessage "Datenverzeichnis: $REDIS_DATA_DIR" -ForegroundColor White
    Write-ColorMessage "Log-Datei: $(Join-Path $LOGS_DIR 'redis.log')" -ForegroundColor White
    Write-ColorMessage "Port: $RedisPort" -ForegroundColor White
    
    Write-ColorMessage "`nVerwenden Sie folgende Befehle zum Starten von Redis:" -ForegroundColor Cyan
    Write-ColorMessage "  cd $REDIS_DIR" -ForegroundColor White
    Write-ColorMessage "  .\redis-server.exe redis.conf" -ForegroundColor White
    Write-ColorMessage "Oder:" -ForegroundColor Cyan
    Write-ColorMessage "  .\start_redis.ps1" -ForegroundColor White
}

# Starte das Hauptprogramm
Main 