# Start-System-Improved.ps1
#
# Dieses Skript startet alle erforderlichen Komponenten des ERP-Systems:
# - Redis-Server
# - Celery-Worker
# - Celery-Flower
# - FastAPI-Server
#
# Verwendung: .\start_system_improved.ps1 [-SkipRedis] [-SkipCelery] [-SkipFlower] [-SkipAPI] [-LogLevel <Level>]
# Parameter:
#   -SkipRedis    : Redis-Server nicht starten
#   -SkipCelery   : Celery-Worker nicht starten
#   -SkipFlower   : Celery-Flower nicht starten
#   -SkipAPI      : API-Server nicht starten
#   -LogLevel     : Log-Level (Verbose, Info, Warning, Error) - Standard: Info

param (
    [switch]$SkipRedis,
    [switch]$SkipCelery,
    [switch]$SkipFlower,
    [switch]$SkipAPI,
    [ValidateSet("Verbose", "Info", "Warning", "Error")]
    [string]$LogLevel = "Info"
)

# Konfiguration
$WORKSPACE_ROOT = "C:\AI_driven_ERP\AI_driven_ERP"
$REDIS_PATH = Join-Path $WORKSPACE_ROOT "redis"
$LOG_DIR = Join-Path $WORKSPACE_ROOT "logs"
$PROCESS_FILE = Join-Path $LOG_DIR "process_info.json"
$ERROR_LOG = Join-Path $LOG_DIR "start_error.log"

# Definiere Log-Farben basierend auf Log-Level
$LogColors = @{
    "Verbose" = "Gray"
    "Info" = "White"
    "Warning" = "Yellow"
    "Error" = "Red"
    "Success" = "Green"
    "Emphasis" = "Cyan"
}

# Funktion für einheitliches Logging
function Write-SystemLog {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [ValidateSet("Verbose", "Info", "Warning", "Error", "Success", "Emphasis")]
        [string]$Level = "Info",
        
        [switch]$NoNewLine,
        
        [switch]$LogToFile
    )
    
    # Log-Level-Filter
    $levelOrder = @{"Verbose" = 0; "Info" = 1; "Warning" = 2; "Error" = 3}
    $currentLevelValue = $levelOrder[$LogLevel]
    $messageLevelValue = $levelOrder[$Level]
    
    # Wenn Level nicht im levelOrder ist (Success/Emphasis), immer anzeigen
    if ($levelOrder.ContainsKey($Level) -and $messageLevelValue -lt $currentLevelValue) {
        return
    }
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = $LogColors[$Level]
    $formattedMessage = "[$timestamp] $Message"
    
    Write-Host $formattedMessage -ForegroundColor $color -NoNewline:$NoNewLine
    
    if ($LogToFile) {
        if ($Level -eq "Error") {
            Add-Content -Path $ERROR_LOG -Value $formattedMessage
        }
        Add-Content -Path (Join-Path $LOG_DIR "system_log.txt") -Value "[$Level] $formattedMessage"
    }
}

# Fehlerbehandlungsfunktion
function Handle-Error {
    param (
        [string]$ComponentName,
        [string]$ErrorMessage,
        [switch]$Fatal
    )
    
    Write-SystemLog "FEHLER bei ${ComponentName}: ${ErrorMessage}" -Level Error -LogToFile
    
    if ($Fatal) {
        Write-SystemLog "Fataler Fehler, breche Skript ab" -Level Error -LogToFile
        Stop-AllProcesses
        exit 1
    }
}

# Erstelle Log-Verzeichnis, falls nicht vorhanden
try {
    if (-not (Test-Path $LOG_DIR)) {
        New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
        Write-SystemLog "Log-Verzeichnis erstellt: $LOG_DIR" -Level Success -LogToFile
    }
} catch {
    Handle-Error -ComponentName "Log-Verzeichnis" -ErrorMessage $_.Exception.Message -Fatal
}

# Prüfe, ob Verzeichnisse existieren
if (-not (Test-Path $WORKSPACE_ROOT)) {
    Handle-Error -ComponentName "Workspace" -ErrorMessage "Workspace-Verzeichnis nicht gefunden: $WORKSPACE_ROOT" -Fatal
}

if (-not $SkipRedis -and -not (Test-Path $REDIS_PATH)) {
    Handle-Error -ComponentName "Redis" -ErrorMessage "Redis-Verzeichnis nicht gefunden: $REDIS_PATH" -Fatal
}

# Aktuelles Datum für Log-Dateien
$DATE = Get-Date -Format "yyyy-MM-dd_HH-mm"

# Log-Dateien definieren
$REDIS_LOG = Join-Path $LOG_DIR "redis_$DATE.log"
$CELERY_LOG = Join-Path $LOG_DIR "celery_$DATE.log"
$FLOWER_LOG = Join-Path $LOG_DIR "flower_$DATE.log"
$API_LOG = Join-Path $LOG_DIR "api_$DATE.log"

# Funktion zum Prüfen, ob ein Dienst läuft
function Test-ServiceRunning {
    param (
        [string]$ServiceName,
        [int]$Port,
        [string]$ProcessName = ""
    )
    
    Write-SystemLog "Prüfe, ob $ServiceName läuft..." -Level Verbose
    
    # Prüfe Prozess, falls angegeben
    if ($ProcessName -ne "") {
        $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        if ($process) {
            Write-SystemLog "$ServiceName läuft bereits (PID: $($process.Id))" -Level Warning -LogToFile
            return $true
        }
    }
    
    # Prüfe Port, falls angegeben
    if ($Port -gt 0) {
        $tcpConnection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($tcpConnection) {
            Write-SystemLog "$ServiceName läuft bereits auf Port $Port (PID: $($tcpConnection.OwningProcess))" -Level Warning -LogToFile
            return $true
        }
    }
    
    return $false
}

# Funktion zum Starten von Prozessen im Hintergrund mit PowerShell
function Start-BackgroundProcess {
    param (
        [string]$Name,
        [string]$Command,
        [string]$LogFile,
        [int]$Port = 0,
        [int]$RetryCount = 3,
        [int]$RetryDelay = 2
    )
    
    Write-SystemLog "Starte $Name..." -Level Emphasis
    
    # Prüfe, ob der Dienst bereits läuft
    if ($Port -gt 0 -and (Test-ServiceRunning -ServiceName $Name -Port $Port)) {
        Write-SystemLog "$Name läuft bereits auf Port $Port - wird wiederverwendet" -Level Warning
        
        # Suche die Prozess-ID für den Port
        $tcpConnection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($tcpConnection) {
            $processId = $tcpConnection.OwningProcess
            try {
                $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($process) {
                    # Füge den existierenden Prozess zu unserem Tracking hinzu
                    Write-SystemLog "Übernehme existierenden Prozess: $Name (PID: $processId)" -Level Success -LogToFile
                    return $process
                }
            } catch {
                Write-SystemLog "Konnte Prozess mit PID $processId nicht finden: $($_.Exception.Message)" -Level Warning -LogToFile
            }
        }
        
        # Wenn wir hierher kommen, ist der Port besetzt, aber wir konnten den Prozess nicht identifizieren
        Write-SystemLog "Port $Port ist belegt, aber der Prozess konnte nicht identifiziert werden" -Level Warning
        return $null
    }
    
    $attempt = 1
    $process = $null
    
    while ($attempt -le $RetryCount -and -not $process) {
        try {
            # Die korrekte Syntax für PowerShell - OHNE -NoExit Parameter
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = "powershell.exe"
            $psi.Arguments = "-Command `"$Command | Tee-Object -FilePath '$LogFile'`""
            $psi.UseShellExecute = $true
            $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Minimized
            
            $process = [System.Diagnostics.Process]::Start($psi)
            
            Write-SystemLog "$Name gestartet (PID: $($process.Id))" -Level Success -LogToFile
        } catch {
            $errorMsg = $_.Exception.Message
            Write-SystemLog "Fehler beim Starten von $Name (Versuch $attempt/$RetryCount): $errorMsg" -Level Warning -LogToFile
            
            if ($attempt -lt $RetryCount) {
                Write-SystemLog "Versuche erneut in $RetryDelay Sekunden..." -Level Info
                Start-Sleep -Seconds $RetryDelay
            } else {
                Handle-Error -ComponentName $Name -ErrorMessage "Konnte nach $RetryCount Versuchen nicht gestartet werden: $errorMsg"
            }
            
            $attempt++
        }
    }
    
    # Prüfe, ob Prozess erfolgreich gestartet wurde
    if ($Port -gt 0 -and $process) {
        # Warte und prüfe, ob der Port geöffnet wird
        $maxWaitTime = 30  # Sekunden
        $waited = 0
        $portOpen = $false
        
        Write-SystemLog "Warte auf Port $Port für $Name..." -Level Verbose
        
        while ($waited -lt $maxWaitTime -and -not $portOpen) {
            Start-Sleep -Seconds 1
            $waited++
            
            $tcpConnection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
            if ($tcpConnection) {
                $portOpen = $true
                Write-SystemLog "$Name ist bereit (Port $Port geöffnet nach $waited Sekunden)" -Level Success
            } elseif ($waited % 5 -eq 0) {
                Write-SystemLog "Warte weiterhin auf $Name (Port $Port)..." -Level Verbose
            }
            
            # Prüfe, ob der Prozess noch läuft
            if ($process.HasExited) {
                Handle-Error -ComponentName $Name -ErrorMessage "Prozess wurde unerwartet beendet (Exit-Code: $($process.ExitCode))"
                return $null
            }
        }
        
        if (-not $portOpen) {
            Handle-Error -ComponentName $Name -ErrorMessage "Port $Port wurde nicht geöffnet innerhalb von $maxWaitTime Sekunden"
        }
    }
    
    return $process
}

# Speichern der Prozessinformationen
function Save-ProcessInfo {
    param (
        [hashtable]$ProcessInfo
    )
    
    try {
        $ProcessInfo | ConvertTo-Json | Set-Content -Path $PROCESS_FILE
        Write-SystemLog "Prozessinformationen gespeichert in $PROCESS_FILE" -Level Verbose -LogToFile
    } catch {
        Write-SystemLog "Fehler beim Speichern der Prozessinformationen: $($_.Exception.Message)" -Level Warning -LogToFile
    }
}

# Wechsle zum Projektverzeichnis
try {
    Set-Location $WORKSPACE_ROOT
    Write-SystemLog "Arbeitsverzeichnis: $WORKSPACE_ROOT" -Level Emphasis
} catch {
    Handle-Error -ComponentName "Set-Location" -ErrorMessage $_.Exception.Message -Fatal
}

# Prozess-Dictionary zum Speichern aller gestarteten Prozesse
$processInfo = @{}

# 1. Redis-Server starten
if (-not $SkipRedis) {
    $redisCommand = "Set-Location '$REDIS_PATH'; .\redis-server.exe"
    $redisProcess = Start-BackgroundProcess -Name "Redis-Server" -Command $redisCommand -LogFile $REDIS_LOG -Port 6379
    
    if ($redisProcess) {
        $processInfo["Redis"] = @{
            "Id" = $redisProcess.Id
            "Name" = "Redis-Server"
            "StartTime" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "LogFile" = $REDIS_LOG
        }
        
        # Warte einen Moment, damit Redis hochfahren kann
        Start-Sleep -Seconds 3
    } else {
        Write-SystemLog "Redis-Server konnte nicht gestartet werden. Einige Komponenten könnten nicht funktionieren." -Level Warning
    }
}

# 2. Celery-Worker starten
if (-not $SkipCelery) {
    if ($SkipRedis) {
        Write-SystemLog "Achtung: Redis wurde übersprungen, Celery könnte Verbindungsprobleme haben" -Level Warning
    }
    
    $celeryCommand = "celery -A backend.tasks.celery_app worker --loglevel=info -n worker1@%computername% -Q default,reports,imports,exports,optimization"
    $celeryProcess = Start-BackgroundProcess -Name "Celery-Worker" -Command $celeryCommand -LogFile $CELERY_LOG
    
    if ($celeryProcess) {
        $processInfo["Celery"] = @{
            "Id" = $celeryProcess.Id
            "Name" = "Celery-Worker"
            "StartTime" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "LogFile" = $CELERY_LOG
        }
        
        # Warte einen Moment, damit Celery hochfahren kann
        Start-Sleep -Seconds 5
    } else {
        Write-SystemLog "Celery-Worker konnte nicht gestartet werden. Task-Verarbeitung wird nicht funktionieren." -Level Warning
    }
}

# 3. Celery-Flower starten
if (-not $SkipFlower) {
    if ($SkipCelery) {
        Write-SystemLog "Achtung: Celery wurde übersprungen, Flower wird keine Daten anzeigen" -Level Warning
    }
    
    $flowerCommand = "celery -A backend.tasks.celery_app flower --port=5555"
    $flowerProcess = Start-BackgroundProcess -Name "Celery-Flower" -Command $flowerCommand -LogFile $FLOWER_LOG -Port 5555
    
    if ($flowerProcess) {
        $processInfo["Flower"] = @{
            "Id" = $flowerProcess.Id
            "Name" = "Celery-Flower"
            "StartTime" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "LogFile" = $FLOWER_LOG
        }
        
        # Warte einen Moment, damit Flower hochfahren kann
        Start-Sleep -Seconds 3
    } else {
        Write-SystemLog "Celery-Flower konnte nicht gestartet werden. Monitoring wird nicht verfügbar sein." -Level Warning
    }
}

# 4. Demo-Server starten (verbesserte Version mit Celery-Unterstützung)
if (-not $SkipAPI) {
    $apiCommand = "uvicorn backend.demo_server_celery_enhanced:app --reload --host 0.0.0.0 --port 8003"
    $apiProcess = Start-BackgroundProcess -Name "Demo-Server" -Command $apiCommand -LogFile $API_LOG -Port 8003
    
    if ($apiProcess) {
        $processInfo["API"] = @{
            "Id" = $apiProcess.Id
            "Name" = "Demo-Server"
            "StartTime" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "LogFile" = $API_LOG
        }
        
        # Warte einen Moment, damit der API-Server hochfahren kann
        Start-Sleep -Seconds 3
    } else {
        Write-SystemLog "Demo-Server konnte nicht gestartet werden. API wird nicht verfügbar sein." -Level Warning
    }
}

# Speichere Prozessinformationen
Save-ProcessInfo -ProcessInfo $processInfo

# System-Status anzeigen
Write-SystemLog "`nERP-System Status:" -Level Emphasis
Write-SystemLog "--------------------------------------" -Level Emphasis

if ($processInfo.ContainsKey("Redis")) {
    Write-SystemLog "Redis-Server     : Aktiv (PID: $($processInfo.Redis.Id)) - localhost:6379" -Level Success
} else {
    $level = "Info"
    if (-not $SkipRedis) {
        $level = "Warning"
    }
    Write-SystemLog "Redis-Server     : Nicht gestartet" -Level $level
}

if ($processInfo.ContainsKey("Celery")) {
    Write-SystemLog "Celery-Worker    : Aktiv (PID: $($processInfo.Celery.Id))" -Level Success
} else {
    $level = "Info"
    if (-not $SkipCelery) {
        $level = "Warning"
    }
    Write-SystemLog "Celery-Worker    : Nicht gestartet" -Level $level
}

if ($processInfo.ContainsKey("Flower")) {
    Write-SystemLog "Celery-Flower UI : Aktiv (PID: $($processInfo.Flower.Id)) - http://localhost:5555" -Level Success
} else {
    $level = "Info"
    if (-not $SkipFlower) {
        $level = "Warning"
    }
    Write-SystemLog "Celery-Flower UI : Nicht gestartet" -Level $level
}

if ($processInfo.ContainsKey("API")) {
    Write-SystemLog "Demo-Server      : Aktiv (PID: $($processInfo.API.Id)) - http://localhost:8003" -Level Success
    Write-SystemLog "API-Dokumentation: http://localhost:8003/docs" -Level Info
} else {
    $level = "Info"
    if (-not $SkipAPI) {
        $level = "Warning"
    }
    Write-SystemLog "Demo-Server      : Nicht gestartet" -Level $level
}

Write-SystemLog "Log-Verzeichnis  : $LOG_DIR" -Level Info
Write-SystemLog "--------------------------------------" -Level Emphasis

# Optionale Funktion zum Beenden aller Prozesse
function Stop-AllProcesses {
    param (
        [switch]$Silent
    )
    
    if (-not $Silent) {
        Write-SystemLog "Beende alle Prozesse..." -Level Warning
    }
    
    foreach ($key in $processInfo.Keys) {
        $id = $processInfo[$key].Id
        $name = $processInfo[$key].Name
        
        try {
            $process = Get-Process -Id $id -ErrorAction SilentlyContinue
            if ($process) {
                Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
                if (-not $Silent) {
                    Write-SystemLog "$name (PID: $id) beendet" -Level Warning -LogToFile
                }
            } else {
                if (-not $Silent) {
                    Write-SystemLog "$name (PID: $id) läuft nicht mehr" -Level Info -LogToFile
                }
            }
        } catch {
            if (-not $Silent) {
                Write-SystemLog "Konnte $name (PID: $id) nicht beenden: $($_.Exception.Message)" -Level Error -LogToFile
            }
        }
    }
    
    # Lösche die Prozessinformation
    if (Test-Path $PROCESS_FILE) {
        Remove-Item -Path $PROCESS_FILE -Force -ErrorAction SilentlyContinue
    }
    
    if (-not $Silent) {
        Write-SystemLog "Alle Prozesse wurden beendet" -Level Success
    }
}

# Zeige Hilfstext
Write-SystemLog "`nVerwenden Sie:" -Level Info
Write-SystemLog " - 'Q' zum Beenden aller Prozesse und Verlassen" -Level Info
Write-SystemLog " - 'R' zum Neustarten aller Prozesse" -Level Info
Write-SystemLog " - 'L' zum Anzeigen der Log-Dateien" -Level Info
Write-SystemLog " - 'S' zum Anzeigen des aktuellen Status" -Level Info
Write-SystemLog " - 'X' zum Verlassen ohne Prozesse zu beenden" -Level Info

# Funktion zum Anzeigen der Log-Dateien
function Show-Logs {
    Write-SystemLog "`nVerfügbare Log-Dateien:" -Level Emphasis
    
    $logFiles = Get-ChildItem -Path $LOG_DIR -Filter "*.log"
    
    for ($i = 0; $i -lt $logFiles.Count; $i++) {
        Write-SystemLog "[$($i+1)] $($logFiles[$i].Name) ($(Get-Date -Date $logFiles[$i].LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss'))" -Level Info
    }
    
    Write-SystemLog "[0] Zurück" -Level Info
    
    $choice = Read-Host "`nWählen Sie eine Log-Datei (0-$($logFiles.Count))"
    
    if ($choice -match '^\d+$' -and [int]$choice -gt 0 -and [int]$choice -le $logFiles.Count) {
        $selectedLog = $logFiles[[int]$choice-1].FullName
        Write-SystemLog "Zeige die letzten 50 Zeilen von $($logFiles[[int]$choice-1].Name):" -Level Emphasis
        Get-Content -Path $selectedLog -Tail 50
        Write-Host "`nDrücken Sie eine Taste, um fortzufahren..."
        [Console]::ReadKey($true) | Out-Null
    }
}

# Funktion zum Anzeigen des aktuellen Status
function Show-Status {
    Write-SystemLog "`nAktueller Status:" -Level Emphasis
    
    foreach ($key in $processInfo.Keys) {
        $id = $processInfo[$key].Id
        $name = $processInfo[$key].Name
        
        try {
            $process = Get-Process -Id $id -ErrorAction SilentlyContinue
            if ($process) {
                $runtime = (Get-Date) - $process.StartTime
                $formattedRuntime = "{0:D2}:{1:D2}:{2:D2}" -f $runtime.Hours, $runtime.Minutes, $runtime.Seconds
                
                Write-SystemLog "$name (PID: $id) - Läuft seit $formattedRuntime - CPU: $($process.CPU) - RAM: $([math]::Round($process.WorkingSet64 / 1MB, 2)) MB" -Level Success
            } else {
                Write-SystemLog "$name (PID: $id) - Nicht mehr aktiv" -Level Warning
            }
        } catch {
            Write-SystemLog "$name (PID: $id) - Status konnte nicht ermittelt werden: $($_.Exception.Message)" -Level Error
        }
    }
}

# Funktion zum Neustarten der Prozesse
function Restart-AllProcesses {
    Write-SystemLog "Starte alle Prozesse neu..." -Level Warning
    
    # Stoppe alle Prozesse
    Stop-AllProcesses -Silent
    
    # Warte einen Moment
    Start-Sleep -Seconds 3
    
    # Starte das Skript neu mit den gleichen Parametern
    $arguments = ""
    if ($SkipRedis) { $arguments += " -SkipRedis" }
    if ($SkipCelery) { $arguments += " -SkipCelery" }
    if ($SkipFlower) { $arguments += " -SkipFlower" }
    if ($SkipAPI) { $arguments += " -SkipAPI" }
    if ($LogLevel -ne "Info") { $arguments += " -LogLevel $LogLevel" }
    
    Start-Process -FilePath "powershell.exe" -ArgumentList "-File `"$($MyInvocation.MyCommand.Path)`"$arguments"
    
    # Beende das aktuelle Skript
    exit 0
}

# Registriere einen Event-Handler für Ctrl+C, um ordnungsgemäß aufzuräumen
try {
    # Diese Zeile funktioniert nur in PowerShell 7+, in PowerShell 5.1 wird sie übersprungen
    $null = [Console]::CancelKeyPress.GetType()
    
    [Console]::CancelKeyPress += {
        param($sender, $e)
        $e.Cancel = $true
        Write-SystemLog "Ctrl+C erkannt, beende Prozesse..." -Level Warning
        Stop-AllProcesses
        exit 0
    }
} catch {
    Write-SystemLog "Hinweis: Erweiterte Ctrl+C-Behandlung nicht verfügbar (benötigt PowerShell 7+)" -Level Verbose
}

# Halte das Skript am Laufen und ermögliche das Beenden aller Prozesse
try {
    while ($true) {
        if ([Console]::KeyAvailable) {
            $key = [Console]::ReadKey($true).Key
            
            switch ($key) {
                'Q' {
                    Write-SystemLog "Beende alle Prozesse und verlasse das Skript..." -Level Warning
                    Stop-AllProcesses
                    exit 0
                }
                'R' {
                    Restart-AllProcesses
                }
                'L' {
                    Show-Logs
                }
                'S' {
                    Show-Status
                }
                'X' {
                    Write-SystemLog "Verlasse die Überwachung. Prozesse laufen weiter im Hintergrund." -Level Warning
                    exit 0
                }
            }
        }
        
        # Prüfe periodisch, ob alle Prozesse noch laufen
        foreach ($key in @($processInfo.Keys)) {  # Verwende eine Kopie der Keys
            $id = $processInfo[$key].Id
            $name = $processInfo[$key].Name
            
            $process = Get-Process -Id $id -ErrorAction SilentlyContinue
            if (-not $process) {
                Write-SystemLog "$name (PID: $id) ist nicht mehr aktiv!" -Level Warning -LogToFile
                $processInfo.Remove($key)
                Save-ProcessInfo -ProcessInfo $processInfo
            }
        }
        
        Start-Sleep -Seconds 2
    }
} finally {
    # Stelle sicher, dass wir den Status speichern, falls das Skript unterbrochen wird
    Save-ProcessInfo -ProcessInfo $processInfo
} 