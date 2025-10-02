# Redis-Setup für erweiterten Cache-Manager
# Dieses Skript prüft, ob Redis installiert ist, installiert es bei Bedarf und konfiguriert es für den Cache-Manager

# Parameter
param (
    [switch]$Install = $false,
    [switch]$ConfigureOnly = $false,
    [string]$RedisPort = "6379",
    [string]$RedisHost = "localhost"
)

# Konstanten
$REDIS_URL = "redis://${RedisHost}:${RedisPort}/0"
$REDIS_WINDOWS_URL = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
$REDIS_DOWNLOAD_PATH = "$env:TEMP\redis.zip"
$REDIS_EXTRACT_PATH = "$env:ProgramFiles\Redis"
$REDIS_CONFIG_PATH = "$env:ProgramFiles\Redis\redis.windows.conf"

# Farbdefinitionen für die Ausgabe
$GREEN = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::Yellow
$RED = [ConsoleColor]::Red
$CYAN = [ConsoleColor]::Cyan

# Funktion zum Prüfen, ob Redis installiert ist
function Test-RedisInstalled {
    try {
        $redisCliPath = "$env:ProgramFiles\Redis\redis-cli.exe"
        if (Test-Path $redisCliPath) {
            Write-Host "Redis-CLI gefunden in: $redisCliPath" -ForegroundColor $GREEN
            return $true
        } else {
            Write-Host "Redis ist nicht installiert oder nicht im erwarteten Pfad." -ForegroundColor $YELLOW
            return $false
        }
    } catch {
        Write-Host "Fehler beim Prüfen der Redis-Installation: $_" -ForegroundColor $RED
        return $false
    }
}

# Funktion zum Prüfen, ob Redis läuft
function Test-RedisRunning {
    param (
        [string]$HostName = $RedisHost,
        [string]$Port = $RedisPort
    )

    try {
        # TCP-Verbindung zum Redis-Port prüfen
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connectResult = $tcpClient.BeginConnect($HostName, [int]$Port, $null, $null)
        $connectSuccess = $connectResult.AsyncWaitHandle.WaitOne(1000, $false)
        
        if ($connectSuccess) {
            $tcpClient.EndConnect($connectResult)
            $tcpClient.Close()
            Write-Host "Redis ist aktiv und erreichbar unter $HostName`:$Port" -ForegroundColor $GREEN
            return $true
        } else {
            Write-Host "Redis ist nicht erreichbar unter $HostName`:$Port" -ForegroundColor $YELLOW
            $tcpClient.Close()
            return $false
        }
    } catch {
        Write-Host "Fehler beim Prüfen des Redis-Status: $_" -ForegroundColor $RED
        return $false
    }
}

# Funktion zum Installieren von Redis unter Windows
function Install-Redis {
    try {
        # Prüfen, ob Redis bereits installiert ist
        if (Test-RedisInstalled) {
            Write-Host "Redis ist bereits installiert." -ForegroundColor $GREEN
            return $true
        }

        Write-Host "Starte Redis-Installation..." -ForegroundColor $CYAN

        # Redis herunterladen
        Write-Host "Lade Redis herunter von $REDIS_WINDOWS_URL..." -ForegroundColor $CYAN
        Invoke-WebRequest -Uri $REDIS_WINDOWS_URL -OutFile $REDIS_DOWNLOAD_PATH

        # Prüfen, ob Download erfolgreich war
        if (-not (Test-Path $REDIS_DOWNLOAD_PATH)) {
            Write-Host "Fehler beim Herunterladen von Redis." -ForegroundColor $RED
            return $false
        }

        # Zielverzeichnis erstellen, falls es nicht existiert
        if (-not (Test-Path $REDIS_EXTRACT_PATH)) {
            New-Item -Path $REDIS_EXTRACT_PATH -ItemType Directory -Force | Out-Null
        }

        # Redis entpacken
        Write-Host "Entpacke Redis nach $REDIS_EXTRACT_PATH..." -ForegroundColor $CYAN
        Expand-Archive -Path $REDIS_DOWNLOAD_PATH -DestinationPath $REDIS_EXTRACT_PATH -Force

        # Prüfen, ob Entpacken erfolgreich war
        if (-not (Test-Path "$REDIS_EXTRACT_PATH\redis-server.exe")) {
            Write-Host "Fehler beim Entpacken von Redis." -ForegroundColor $RED
            return $false
        }

        # Redis als Windows-Dienst einrichten
        Write-Host "Richte Redis als Windows-Dienst ein..." -ForegroundColor $CYAN
        $redisSvcPath = "$REDIS_EXTRACT_PATH\redis-server.exe"
        Start-Process -FilePath $redisSvcPath -ArgumentList "--service-install $REDIS_CONFIG_PATH" -Wait -NoNewWindow

        # Redis-Dienst starten
        Write-Host "Starte Redis-Dienst..." -ForegroundColor $CYAN
        Start-Process -FilePath $redisSvcPath -ArgumentList "--service-start" -Wait -NoNewWindow

        # Temporäre Dateien aufräumen
        if (Test-Path $REDIS_DOWNLOAD_PATH) {
            Remove-Item -Path $REDIS_DOWNLOAD_PATH -Force
        }

        Write-Host "Redis wurde erfolgreich installiert und gestartet." -ForegroundColor $GREEN
        return $true
    } catch {
        Write-Host "Fehler bei der Redis-Installation: $_" -ForegroundColor $RED
        return $false
    }
}

# Funktion zum Konfigurieren des Python-Redis-Pakets
function Configure-PythonRedis {
    try {
        Write-Host "Prüfe, ob das Python-Redis-Paket installiert ist..." -ForegroundColor $CYAN
        $pipResult = python -m pip show redis 2>&1
        
        if ($LASTEXITCODE -ne 0 -or $pipResult -match "not found") {
            Write-Host "Installiere das Python-Redis-Paket..." -ForegroundColor $CYAN
            python -m pip install redis
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Fehler beim Installieren des Python-Redis-Pakets." -ForegroundColor $RED
                return $false
            }
        } else {
            Write-Host "Python-Redis-Paket ist bereits installiert." -ForegroundColor $GREEN
        }
        
        return $true
    } catch {
        Write-Host "Fehler beim Konfigurieren des Python-Redis-Pakets: $_" -ForegroundColor $RED
        return $false
    }
}

# Funktion zum Aktualisieren der Cache-Konfiguration im Projekt
function Update-CacheConfig {
    try {
        $enhancedCacheManagerPath = Join-Path (Get-Location) "backend\enhanced_cache_manager.py"
        
        if (-not (Test-Path $enhancedCacheManagerPath)) {
            Write-Host "enhanced_cache_manager.py nicht gefunden in $enhancedCacheManagerPath" -ForegroundColor $RED
            return $false
        }
        
        Write-Host "Aktualisiere Cache-Konfiguration in $enhancedCacheManagerPath..." -ForegroundColor $CYAN
        
        # Dateiinhalt lesen
        $content = Get-Content -Path $enhancedCacheManagerPath -Raw
        
        # Aktive Cache-Instanz mit Redis konfigurieren
        $redisConfigLine = "# redis_cache = EnhancedCacheManager(backend=`"redis`", redis_url=`"redis://localhost:6379/0`")"
        $newRedisConfigLine = "redis_cache = EnhancedCacheManager(backend=`"redis`", redis_url=`"$REDIS_URL`")"
        
        if ($content -match [regex]::Escape($redisConfigLine)) {
            $content = $content -replace [regex]::Escape($redisConfigLine), $newRedisConfigLine
            Set-Content -Path $enhancedCacheManagerPath -Value $content
            Write-Host "Redis-Cache-Konfiguration aktiviert." -ForegroundColor $GREEN
        } else {
            Write-Host "Konfigurationszeile für Redis-Cache nicht gefunden oder bereits aktiviert." -ForegroundColor $YELLOW
        }
        
        return $true
    } catch {
        Write-Host "Fehler beim Aktualisieren der Cache-Konfiguration: $_" -ForegroundColor $RED
        return $false
    }
}

# Funktion zum Testen der Redis-Verbindung mit Python
function Test-RedisPython {
    try {
        $testCode = @"
import redis
import sys

try:
    r = redis.from_url('$REDIS_URL')
    r.ping()
    r.set('test_key', 'Hello from Python')
    value = r.get('test_key')
    print("Redis-Test erfolgreich: {}".format(value))
    sys.exit(0)
except Exception as e:
    print("Redis-Verbindungsfehler: {}".format(e))
    sys.exit(1)
"@
        
        Write-Host "Teste Redis-Verbindung mit Python..." -ForegroundColor $CYAN
        $testFile = "$env:TEMP\redis_test.py"
        Set-Content -Path $testFile -Value $testCode
        
        $result = python $testFile
        if ($LASTEXITCODE -eq 0) {
            Write-Host $result -ForegroundColor $GREEN
            Remove-Item -Path $testFile -Force
            return $true
        } else {
            Write-Host $result -ForegroundColor $RED
            Remove-Item -Path $testFile -Force
            return $false
        }
    } catch {
        Write-Host "Fehler beim Testen der Redis-Verbindung: $_" -ForegroundColor $RED
        if (Test-Path "$env:TEMP\redis_test.py") {
            Remove-Item -Path "$env:TEMP\redis_test.py" -Force
        }
        return $false
    }
}

# Funktion zum Erstellen einer Beispiel-Verwendung
function Create-Example {
    try {
        $exampleFile = Join-Path (Get-Location) "backend\examples\cache_example.py"
        $exampleDir = Split-Path -Parent $exampleFile
        
        if (-not (Test-Path $exampleDir)) {
            New-Item -Path $exampleDir -ItemType Directory -Force | Out-Null
        }
        
        $exampleCode = @"
"""
Beispiel für die Verwendung des erweiterten Cache-Managers
"""

import asyncio
import time
from enhanced_cache_manager import cache, redis_cache

# Cache-Instanz für das Beispiel auswählen
# Kommentare ändern, um zwischen Memory und Redis zu wechseln
active_cache = cache  # Memory-Cache
# active_cache = redis_cache  # Redis-Cache

# Beispielfunktion mit Cache-Dekorator
@active_cache.cached(ttl=60, tags=["example", "articles"])
async def get_articles(category=None, limit=10):
    """
    Diese Funktion gibt Beispiel-Artikel zurück und simuliert eine langsame Operation
    Bei wiederholten Aufrufen mit den gleichen Parametern wird das Ergebnis aus dem Cache geladen
    """
    print("Lade Artikel für Kategorie '{}' (Limit: {})...".format(category, limit))
    
    # Simuliere langsame Datenbankabfrage
    await asyncio.sleep(2)
    
    # Dummy-Daten
    articles = [
        {"id": i, "title": "Artikel {}".format(i), "category": category or "allgemein"}
        for i in range(1, limit + 1)
    ]
    
    print("{} Artikel geladen.".format(len(articles)))
    return articles

# Funktion zum Testen der Tag-Invalidierung
async def test_tag_invalidation():
    """
    Demonstriert die Verwendung von Tag-Invalidierung
    """
    # Ersten Aufruf ausführen (wird aus der Datenbank geladen)
    articles1 = await get_articles(category="technik", limit=5)
    print("Erstes Ergebnis: {} Artikel".format(len(articles1)))
    
    # Zweiten Aufruf ausführen (sollte aus dem Cache kommen)
    start_time = time.time()
    articles2 = await get_articles(category="technik", limit=5)
    elapsed = time.time() - start_time
    print("Zweites Ergebnis: {} Artikel, Dauer: {:.4f}s (sollte schnell sein)".format(len(articles2), elapsed))
    
    # Tag invalidieren
    print("Invalidiere Tag 'articles'...")
    invalidated = active_cache.invalidate_tag("articles")
    print("{} Cache-Einträge invalidiert".format(invalidated))
    
    # Dritten Aufruf ausführen (sollte wieder aus der Datenbank kommen)
    start_time = time.time()
    articles3 = await get_articles(category="technik", limit=5)
    elapsed = time.time() - start_time
    print("Drittes Ergebnis: {} Artikel, Dauer: {:.4f}s (sollte langsam sein)".format(len(articles3), elapsed))
    
    # Cache-Statistiken anzeigen
    stats = active_cache.get_stats()
    print("Cache-Statistiken: {}".format(stats))

# Hauptfunktion
async def main():
    print("=== Erweiterter Cache-Manager - Beispiel ===")
    backend_type = 'Redis-Cache' if active_cache._backend == 'redis' else 'Memory-Cache'
    print("Verwende {}".format(backend_type))
    
    # Beispiel für normale Cache-Verwendung
    print("\n--- Beispiel 1: Grundlegende Cache-Verwendung ---")
    await test_basic_caching()
    
    # Beispiel für Tag-Invalidierung
    print("\n--- Beispiel 2: Tag-Invalidierung ---")
    await test_tag_invalidation()

async def test_basic_caching():
    """
    Demonstriert die grundlegende Cache-Verwendung
    """
    # Ersten Aufruf ausführen (wird aus der Datenbank geladen)
    start_time = time.time()
    result1 = await get_articles(category="news", limit=3)
    elapsed1 = time.time() - start_time
    print("Erster Aufruf: {} Artikel, Dauer: {:.4f}s".format(len(result1), elapsed1))
    
    # Zweiten Aufruf mit denselben Parametern ausführen (sollte aus dem Cache kommen)
    start_time = time.time()
    result2 = await get_articles(category="news", limit=3)
    elapsed2 = time.time() - start_time
    print("Zweiter Aufruf: {} Artikel, Dauer: {:.4f}s".format(len(result2), elapsed2))
    print("Cache-Beschleunigung: {:.1f}x schneller".format(elapsed1 / elapsed2))
    
    # Aufruf mit anderen Parametern (sollte aus der Datenbank kommen)
    start_time = time.time()
    result3 = await get_articles(category="news", limit=5)
    elapsed3 = time.time() - start_time
    print("Aufruf mit anderen Parametern: {} Artikel, Dauer: {:.4f}s".format(len(result3), elapsed3))

if __name__ == "__main__":
    asyncio.run(main())
"@
        
        Set-Content -Path $exampleFile -Value $exampleCode
        Write-Host "Beispiel erstellt: $exampleFile" -ForegroundColor $GREEN
        return $true
    } catch {
        Write-Host "Fehler beim Erstellen des Beispiels: $_" -ForegroundColor $RED
        return $false
    }
}

# Hauptfunktion
function Main {
    Write-Host "=== Redis-Setup für den erweiterten Cache-Manager ===" -ForegroundColor $CYAN
    Write-Host "Host: $RedisHost, Port: $RedisPort" -ForegroundColor $CYAN
    Write-Host "Redis-URL: $REDIS_URL" -ForegroundColor $CYAN
    Write-Host ""
    
    $redisInstalled = Test-RedisInstalled
    $redisRunning = Test-RedisRunning
    
    if ($Install -and -not $redisInstalled) {
        Install-Redis
        $redisInstalled = Test-RedisInstalled
        $redisRunning = Test-RedisRunning
    }
    
    if (-not $redisInstalled -and -not $ConfigureOnly) {
        Write-Host "Redis ist nicht installiert. Verwenden Sie den Parameter -Install, um Redis zu installieren." -ForegroundColor $YELLOW
        return
    }
    
    if (-not $redisRunning -and -not $ConfigureOnly) {
        Write-Host "Redis ist nicht erreichbar. Stelle sicher, dass der Redis-Server läuft." -ForegroundColor $YELLOW
        return
    }
    
    # Python-Redis-Paket konfigurieren
    $pythonRedisConfigured = Configure-PythonRedis
    
    if (-not $pythonRedisConfigured) {
        Write-Host "Fehler beim Konfigurieren des Python-Redis-Pakets." -ForegroundColor $RED
        return
    }
    
    # Cache-Konfiguration aktualisieren
    $cacheConfigUpdated = Update-CacheConfig
    
    if (-not $cacheConfigUpdated) {
        Write-Host "Fehler beim Aktualisieren der Cache-Konfiguration." -ForegroundColor $RED
        return
    }
    
    # Redis-Verbindung mit Python testen
    if (-not $ConfigureOnly) {
        $redisPythonTest = Test-RedisPython
        
        if (-not $redisPythonTest) {
            Write-Host "Redis-Verbindungstest mit Python fehlgeschlagen." -ForegroundColor $RED
            return
        }
    }
    
    # Beispiel erstellen
    Create-Example
    
    Write-Host ""
    Write-Host "=== Redis-Setup für den erweiterten Cache-Manager abgeschlossen ===" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "Verwenden Sie die folgenden Befehle, um das Beispiel auszuführen:" -ForegroundColor $CYAN
    Write-Host "cd $(Get-Location)" -ForegroundColor $CYAN
    Write-Host "python backend\examples\cache_example.py" -ForegroundColor $CYAN
}

# Skript ausführen
Main 