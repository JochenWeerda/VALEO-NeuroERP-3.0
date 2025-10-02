# Start-System.ps1
#
# Dieses Skript startet alle erforderlichen Komponenten des ERP-Systems:
# - Redis-Server
# - Celery-Worker
# - Celery-Flower
# - FastAPI-Server
#
# Verwendung: .\start_system.ps1

# Konfiguration
$WORKSPACE_ROOT = "C:\AI_driven_ERP\AI_driven_ERP"
$REDIS_PATH = Join-Path $WORKSPACE_ROOT "redis"
$LOG_DIR = Join-Path $WORKSPACE_ROOT "logs"

# Erstelle Log-Verzeichnis, falls nicht vorhanden
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR
    Write-Host "Log-Verzeichnis erstellt: $LOG_DIR"
}

# Aktuelles Datum für Log-Dateien
$DATE = Get-Date -Format "yyyy-MM-dd_HH-mm"

# Log-Dateien definieren
$REDIS_LOG = Join-Path $LOG_DIR "redis_$DATE.log"
$CELERY_LOG = Join-Path $LOG_DIR "celery_$DATE.log"
$FLOWER_LOG = Join-Path $LOG_DIR "flower_$DATE.log"
$API_LOG = Join-Path $LOG_DIR "api_$DATE.log"

# Funktion zum Starten von Prozessen im Hintergrund
function Start-BackgroundProcess {
    param (
        [string]$Name,
        [string]$Command,
        [string]$LogFile
    )
    
    Write-Host "Starte $Name..." -ForegroundColor Green
    # Start-Process verwendet nicht -NoExit, da dieser Parameter für PowerShell.exe und nicht für Start-Process ist
    Start-Process powershell -ArgumentList "-Command `"$Command | Tee-Object -FilePath '$LogFile'`"" -WindowStyle Minimized
}

# Alternative Funktion zum Starten von PowerShell-Instanzen im neuen Fenster
function Start-PowerShellProcess {
    param (
        [string]$Name,
        [string]$Command,
        [string]$LogFile
    )
    
    Write-Host "Starte $Name..." -ForegroundColor Green
    # PowerShell direkt aufrufen mit korrekten Parametern
    powershell.exe -NoExit -Command "$Command | Tee-Object -FilePath '$LogFile'"
}

# Wechsle zum Projektverzeichnis
Set-Location $WORKSPACE_ROOT
Write-Host "Arbeitsverzeichnis: $WORKSPACE_ROOT" -ForegroundColor Cyan

# 1. Redis-Server starten
$redisCommand = "Set-Location '$REDIS_PATH'; .\redis-server.exe"
Start-BackgroundProcess -Name "Redis-Server" -Command $redisCommand -LogFile $REDIS_LOG

# Warte einen Moment, damit Redis hochfahren kann
Start-Sleep -Seconds 3
Write-Host "Redis-Server gestartet" -ForegroundColor Green

# 2. Celery-Worker starten
$celeryCommand = "celery -A backend.tasks.celery_app worker --loglevel=info -n worker1@%computername% -Q default,reports,imports,exports,optimization"
Start-BackgroundProcess -Name "Celery-Worker" -Command $celeryCommand -LogFile $CELERY_LOG

# Warte einen Moment, damit Celery hochfahren kann
Start-Sleep -Seconds 5
Write-Host "Celery-Worker gestartet" -ForegroundColor Green

# 3. Celery-Flower starten
$flowerCommand = "celery -A backend.tasks.celery_app flower --port=5555"
Start-BackgroundProcess -Name "Celery-Flower" -Command $flowerCommand -LogFile $FLOWER_LOG

# Warte einen Moment, damit Flower hochfahren kann
Start-Sleep -Seconds 3
Write-Host "Celery-Flower gestartet (http://localhost:5555)" -ForegroundColor Green

# 4. FastAPI-Server starten
$apiCommand = "uvicorn backend.modular_server:app --reload --host 0.0.0.0 --port 8000"
Start-BackgroundProcess -Name "FastAPI-Server" -Command $apiCommand -LogFile $API_LOG

# Warte einen Moment, damit der API-Server hochfahren kann
Start-Sleep -Seconds 3
Write-Host "FastAPI-Server gestartet (http://localhost:8000)" -ForegroundColor Green

# System-Status anzeigen
Write-Host "`nERP-System erfolgreich gestartet!" -ForegroundColor Cyan
Write-Host "--------------------------------------" -ForegroundColor Cyan
Write-Host "Redis-Server     : localhost:6379" -ForegroundColor White
Write-Host "Celery-Worker    : Aktiv (siehe Logs)" -ForegroundColor White
Write-Host "Celery-Flower UI : http://localhost:5555" -ForegroundColor White
Write-Host "FastAPI-Server   : http://localhost:8000" -ForegroundColor White
Write-Host "API-Dokumentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Log-Verzeichnis  : $LOG_DIR" -ForegroundColor White
Write-Host "--------------------------------------" -ForegroundColor Cyan
Write-Host "Verwenden Sie Ctrl+C in den jeweiligen Fenstern, um die Dienste zu beenden."
Write-Host "Alle Log-Dateien werden im Verzeichnis $LOG_DIR gespeichert." 