# System-Test.ps1
#
# Dieses Skript führt automatisierte Tests für alle Komponenten des ERP-Systems durch:
# - Überprüft Redis-Verfügbarkeit
# - Testet Celery-Worker-Konnektivität
# - Überprüft API-Endpunkte
# - Testet Datenbankverbindungen
# - Validiert Module und Klassen
#
# Verwendung: .\system_test.ps1 [-Verbose]
# Parameter:
#   -Verbose    : Zeigt detaillierte Testinformationen

param (
    [switch]$Verbose
)

# Konfiguration
$WORKSPACE_ROOT = "C:\AI_driven_ERP\AI_driven_ERP"
$LOG_DIR = Join-Path $WORKSPACE_ROOT "logs"
$TEST_LOG = Join-Path $LOG_DIR "system_test_$(Get-Date -Format 'yyyy-MM-dd_HH-mm').log"
$REDIS_PORT = 6379
$API_PORT = 8003
$FLOWER_PORT = 5555

# Farbdefinitionen
$Colors = @{
    "Success" = "Green"
    "Warning" = "Yellow"
    "Error" = "Red"
    "Info" = "Cyan"
    "Detail" = "Gray"
}

# Stelle sicher, dass Log-Verzeichnis existiert
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# Funktion für einheitliches Logging
function Write-TestLog {
    param (
        [string]$Message,
        [string]$Level = "Info",
        [switch]$NoLog
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = $Colors[$Level]
    $logMessage = "[$timestamp] [$Level] $Message"
    
    Write-Host $logMessage -ForegroundColor $color
    
    if (-not $NoLog) {
        Add-Content -Path $TEST_LOG -Value $logMessage
    }
}

# Testfunktion für Redis
function Test-Redis {
    Write-TestLog "Teste Redis-Server..." -Level "Info"
    
    try {
        $tcpConnection = Get-NetTCPConnection -LocalPort $REDIS_PORT -ErrorAction SilentlyContinue
        
        if ($tcpConnection) {
            $processId = $tcpConnection.OwningProcess
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            
            if ($process) {
                Write-TestLog "Redis-Server läuft (PID: $processId, Prozess: $($process.ProcessName))" -Level "Success"
                return $true
            } else {
                Write-TestLog "Port $REDIS_PORT ist belegt, aber kein Redis-Prozess gefunden" -Level "Warning"
            }
        } else {
            Write-TestLog "Redis-Server ist nicht aktiv (Port $REDIS_PORT nicht belegt)" -Level "Error"
        }
    } catch {
        Write-TestLog "Fehler beim Testen des Redis-Servers: $($_.Exception.Message)" -Level "Error"
    }
    
    return $false
}

# Testfunktion für API-Server
function Test-APIServer {
    Write-TestLog "Teste API-Server..." -Level "Info"
    
    try {
        # Prüfe, ob Port aktiv ist
        $tcpConnection = Get-NetTCPConnection -LocalPort $API_PORT -ErrorAction SilentlyContinue
        
        if (-not $tcpConnection) {
            Write-TestLog "API-Server ist nicht aktiv (Port $API_PORT nicht belegt)" -Level "Error"
            return $false
        }
        
        # Teste API-Endpunkte
        $endpoints = @(
            @{Uri = "http://localhost:$API_PORT/health"; Name = "Gesundheitscheck"},
            @{Uri = "http://localhost:$API_PORT/api/stats"; Name = "Statistiken"},
            @{Uri = "http://localhost:$API_PORT/"; Name = "Root"}
        )
        
        $allEndpointsSuccessful = $true
        
        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint.Uri -UseBasicParsing
                
                if ($response.StatusCode -eq 200) {
                    Write-TestLog "Endpunkt '$($endpoint.Name)' erfolgreich getestet (Status: $($response.StatusCode))" -Level "Success"
                    
                    if ($Verbose) {
                        Write-TestLog "Antwort: $($response.Content)" -Level "Detail"
                    }
                } else {
                    Write-TestLog "Endpunkt '$($endpoint.Name)' gab unerwarteten Status zurück: $($response.StatusCode)" -Level "Warning"
                    $allEndpointsSuccessful = $false
                }
            } catch {
                Write-TestLog "Fehler beim Aufrufen des Endpunkts '$($endpoint.Name)': $($_.Exception.Message)" -Level "Error"
                $allEndpointsSuccessful = $false
            }
        }
        
        # Erstelle und teste einen Task
        try {
            $body = @{
                task_type = "report"
                parameters = @{
                    report_name = "test_report"
                }
            } | ConvertTo-Json
            
            $response = Invoke-WebRequest -Uri "http://localhost:$API_PORT/api/tasks" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
            
            if ($response.StatusCode -eq 200) {
                $taskResult = $response.Content | ConvertFrom-Json
                Write-TestLog "Task-Erstellung erfolgreich (Task-ID: $($taskResult.task_id))" -Level "Success"
                
                # Prüfe den Task-Status
                Start-Sleep -Seconds 2
                $statusResponse = Invoke-WebRequest -Uri "http://localhost:$API_PORT/api/tasks/$($taskResult.task_id)" -UseBasicParsing
                $taskStatus = $statusResponse.Content | ConvertFrom-Json
                
                Write-TestLog "Task-Status: $($taskStatus.status)" -Level "Success"
                
                if ($Verbose) {
                    Write-TestLog "Task-Details: $($statusResponse.Content)" -Level "Detail"
                }
            } else {
                Write-TestLog "Task-Erstellung gab unerwarteten Status zurück: $($response.StatusCode)" -Level "Warning"
                $allEndpointsSuccessful = $false
            }
        } catch {
            Write-TestLog "Fehler bei der Task-Erstellung: $($_.Exception.Message)" -Level "Error"
            $allEndpointsSuccessful = $false
        }
        
        return $allEndpointsSuccessful
    } catch {
        Write-TestLog "Fehler beim Testen des API-Servers: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

# Testfunktion für Python-Module
function Test-PythonModules {
    Write-TestLog "Teste Python-Module und Klassen..." -Level "Info"
    
    $testScript = @"
import sys
import importlib
from pathlib import Path

# Zu testende Module und Klassen
modules_to_test = [
    "backend.api.batch_processing",
    "backend.api.performance",
    "backend.models.lager",
    "backend.models.partner",
    "backend.models.produktion",
    "backend.models.user",
    "backend.models.notfall",
    "backend.db.performance_monitor"
]

classes_to_test = {
    "backend.models.lager": ["LagerOrt"],
    "backend.models.partner": ["KundenGruppe"],
    "backend.models.produktion": ["ProduktionsAuftrag"],
    "backend.models.user": ["Permission"],
    "backend.models.notfall": ["NotfallPlan"],
    "backend.db.performance_monitor": ["DBPerformanceMiddleware"]
}

# SQLAlchemy JSONB Test
def test_sqlalchemy_jsonb():
    try:
        # Versuche, JSONB aus backend.db zu importieren
        from backend.db import JSONB
        print("[SUCCESS] SQLAlchemy JSONB-Patch wurde erfolgreich angewendet")
        return True
    except ImportError as e:
        print(f"[ERROR] SQLAlchemy JSONB-Patch nicht verfügbar: {str(e)}")
        return False

# Teste Module
def test_modules():
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"[SUCCESS] Modul {module_name} erfolgreich importiert")
            success_count += 1
        except ImportError as e:
            print(f"[ERROR] Modul {module_name} konnte nicht importiert werden: {str(e)}")
    
    return success_count, total_count

# Teste Klassen
def test_classes():
    success_count = 0
    total_count = sum(len(classes) for classes in classes_to_test.values())
    
    for module_name, class_names in classes_to_test.items():
        try:
            module = importlib.import_module(module_name)
            
            for class_name in class_names:
                try:
                    cls = getattr(module, class_name)
                    print(f"[SUCCESS] Klasse {module_name}.{class_name} erfolgreich importiert")
                    success_count += 1
                except AttributeError as e:
                    print(f"[ERROR] Klasse {module_name}.{class_name} nicht gefunden: {str(e)}")
        except ImportError as e:
            print(f"[ERROR] Modul {module_name} konnte nicht importiert werden: {str(e)}")
            # Zähle alle Klassen in diesem Modul als fehlgeschlagen
            pass
    
    return success_count, total_count

# Führe Tests aus
if __name__ == "__main__":
    print("=== Python-Modul- und Klassentests ===")
    
    # Teste JSONB
    jsonb_success = test_sqlalchemy_jsonb()
    
    # Teste Module
    module_success, module_total = test_modules()
    print(f"Module: {module_success}/{module_total} erfolgreich")
    
    # Teste Klassen
    class_success, class_total = test_classes()
    print(f"Klassen: {class_success}/{class_total} erfolgreich")
    
    # Gesamtergebnis
    total_success = module_success + class_success + (1 if jsonb_success else 0)
    total_tests = module_total + class_total + 1
    
    print(f"=== Gesamtergebnis: {total_success}/{total_tests} Tests erfolgreich ===")
    
    # Setze Exit-Code basierend auf Testergebnissen
    if total_success == total_tests:
        print("[SUCCESS] Alle Tests bestanden")
        sys.exit(0)
    else:
        print("[WARNING] Einige Tests sind fehlgeschlagen")
        sys.exit(1)
"@
    
    # Speichere das Testskript temporär
    $tempScriptPath = Join-Path $WORKSPACE_ROOT "temp_module_test.py"
    $testScript | Out-File -FilePath $tempScriptPath -Encoding utf8
    
    try {
        # Führe das Testskript aus
        Write-TestLog "Führe Python-Modul-Tests aus..." -Level "Info"
        $results = & python $tempScriptPath
        
        # Analysiere Ergebnisse
        $successCount = 0
        $errorCount = 0
        
        foreach ($line in $results) {
            if ($line -match "\[SUCCESS\]") {
                Write-TestLog $line -Level "Success"
                $successCount++
            } elseif ($line -match "\[ERROR\]") {
                Write-TestLog $line -Level "Error"
                $errorCount++
            } elseif ($line -match "\[WARNING\]") {
                Write-TestLog $line -Level "Warning"
            } else {
                Write-TestLog $line -Level "Info"
            }
        }
        
        # Überprüfe Gesamtergebnis
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 0) {
            Write-TestLog "Alle Python-Modul-Tests erfolgreich" -Level "Success"
            return $true
        } else {
            Write-TestLog "Einige Python-Modul-Tests sind fehlgeschlagen" -Level "Warning"
            return $false
        }
    } catch {
        Write-TestLog "Fehler bei der Ausführung des Python-Modultests: $($_.Exception.Message)" -Level "Error"
        return $false
    } finally {
        # Entferne das temporäre Skript
        if (Test-Path $tempScriptPath) {
            Remove-Item -Path $tempScriptPath -Force
        }
    }
}

# Testfunktion für Celery
function Test-Celery {
    Write-TestLog "Teste Celery und Flower..." -Level "Info"
    
    # Prüfe Flower
    try {
        $tcpConnection = Get-NetTCPConnection -LocalPort $FLOWER_PORT -ErrorAction SilentlyContinue
        
        if ($tcpConnection) {
            $processId = $tcpConnection.OwningProcess
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            
            if ($process) {
                Write-TestLog "Celery-Flower läuft (PID: $processId, Prozess: $($process.ProcessName))" -Level "Success"
                
                # Teste Flower-API
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:$FLOWER_PORT/api/workers" -UseBasicParsing
                    
                    if ($response.StatusCode -eq 200) {
                        Write-TestLog "Flower-API erfolgreich getestet" -Level "Success"
                        
                        if ($Verbose) {
                            Write-TestLog "Verfügbare Worker: $($response.Content)" -Level "Detail"
                        }
                        
                        # Prüfe, ob Worker verfügbar sind
                        $workers = $response.Content | ConvertFrom-Json
                        
                        if ($workers.PSObject.Properties.Count -gt 0) {
                            Write-TestLog "Celery-Worker sind verfügbar" -Level "Success"
                            return $true
                        } else {
                            Write-TestLog "Keine Celery-Worker gefunden" -Level "Warning"
                        }
                    } else {
                        Write-TestLog "Flower-API gab unerwarteten Status zurück: $($response.StatusCode)" -Level "Warning"
                    }
                } catch {
                    Write-TestLog "Fehler beim Aufrufen der Flower-API: $($_.Exception.Message)" -Level "Error"
                }
            } else {
                Write-TestLog "Port $FLOWER_PORT ist belegt, aber kein Flower-Prozess gefunden" -Level "Warning"
            }
        } else {
            Write-TestLog "Celery-Flower ist nicht aktiv (Port $FLOWER_PORT nicht belegt)" -Level "Error"
        }
    } catch {
        Write-TestLog "Fehler beim Testen von Celery: $($_.Exception.Message)" -Level "Error"
    }
    
    return $false
}

# Führe alle Tests aus
function Run-AllTests {
    Write-TestLog "=== ERP-System-Test gestartet $(Get-Date) ===" -Level "Info"
    
    $allTestsPassed = $true
    $results = @{}
    
    # Test 1: Redis
    $results["Redis"] = Test-Redis
    $allTestsPassed = $allTestsPassed -and $results["Redis"]
    
    # Test 2: API-Server
    $results["APIServer"] = Test-APIServer
    $allTestsPassed = $allTestsPassed -and $results["APIServer"]
    
    # Test 3: Python-Module
    $results["PythonModules"] = Test-PythonModules
    $allTestsPassed = $allTestsPassed -and $results["PythonModules"]
    
    # Test 4: Celery
    $results["Celery"] = Test-Celery
    $allTestsPassed = $allTestsPassed -and $results["Celery"]
    
    # Zusammenfassung
    Write-TestLog "`n=== Testergebnisse ===" -Level "Info"
    
    foreach ($test in $results.Keys) {
        $status = if ($results[$test]) { "BESTANDEN" } else { "FEHLGESCHLAGEN" }
        $level = if ($results[$test]) { "Success" } else { "Error" }
        Write-TestLog "$test-Test: $status" -Level $level
    }
    
    if ($allTestsPassed) {
        Write-TestLog "`nALLE TESTS ERFOLGREICH BESTANDEN!" -Level "Success"
    } else {
        Write-TestLog "`nEINIGE TESTS SIND FEHLGESCHLAGEN! Siehe Log für Details: $TEST_LOG" -Level "Error"
    }
    
    Write-TestLog "=== Test abgeschlossen $(Get-Date) ===" -Level "Info"
    
    return $allTestsPassed
}

# Hauptausführung
if ($Verbose) {
    Write-TestLog "Ausführlicher Modus aktiviert" -Level "Info"
}

Set-Location $WORKSPACE_ROOT
$testResult = Run-AllTests

# Setze Exit-Code basierend auf Testergebnis
exit [int](-not $testResult) 