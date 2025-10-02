# Wiederherstellungs-Skript für das APM Multi-Agenten-System
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupDate,
    [string]$Namespace = "valeo-neuroerp",
    [switch]$RestoreMemoryBank,
    [switch]$RestoreMongoDB,
    [switch]$SkipConfirmation
)

# Funktion zum Überprüfen der Voraussetzungen
function Test-Prerequisites {
    Write-Host "Überprüfe Voraussetzungen..." -ForegroundColor Yellow
    
    # Kubectl überprüfen
    if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
        throw "kubectl nicht gefunden. Bitte installieren Sie kubectl."
    }
    
    # MongoDB-Tools überprüfen
    if (!(Get-Command mongorestore -ErrorAction SilentlyContinue)) {
        throw "mongorestore nicht gefunden. Bitte installieren Sie MongoDB Database Tools."
    }
    
    Write-Host "✓ Voraussetzungen erfüllt" -ForegroundColor Green
}

# Funktion zum Herunterfahren des Systems
function Stop-APMSystem {
    Write-Host "Fahre APM-System herunter..." -ForegroundColor Yellow
    
    kubectl scale deployment apm-multi-agent --replicas=0 -n $Namespace
    
    # Warten bis alle Pods beendet sind
    $maxAttempts = 30
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        $pods = kubectl get pods -n $Namespace -l app=apm-multi-agent -o jsonpath='{.items[*].status.phase}'
        if ($pods -eq "") {
            break
        }
        $attempt++
        Write-Host "Warte auf Beendigung der Pods... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
    
    Write-Host "✓ System heruntergefahren" -ForegroundColor Green
}

# Funktion zum Wiederherstellen der Memory Bank
function Restore-MemoryBank {
    Write-Host "Stelle Memory Bank wieder her..." -ForegroundColor Yellow
    
    $backupFile = "memory-bank-$BackupDate.tar.gz"
    $podName = kubectl get pod -n $Namespace -l app=apm-multi-agent -o jsonpath='{.items[0].metadata.name}'
    
    # Backup in Pod kopieren
    kubectl cp "backups/$backupFile" "$Namespace/$podName:/tmp/$backupFile"
    
    # Backup entpacken
    kubectl exec -n $Namespace $podName -- tar xzf "/tmp/$backupFile" -C /
    
    Write-Host "✓ Memory Bank wiederhergestellt" -ForegroundColor Green
}

# Funktion zum Wiederherstellen der MongoDB
function Restore-MongoDB {
    Write-Host "Stelle MongoDB wieder her..." -ForegroundColor Yellow
    
    $backupFile = "mongodb-$BackupDate.gz"
    
    # MongoDB-URI aus Secret holen
    $mongodbUri = kubectl get secret mongodb-credentials -n $Namespace -o jsonpath='{.data.uri}' | 
                  ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
    
    # Backup wiederherstellen
    mongorestore --uri="$mongodbUri" --gzip --archive="backups/$backupFile"
    
    Write-Host "✓ MongoDB wiederhergestellt" -ForegroundColor Green
}

# Funktion zum Starten des Systems
function Start-APMSystem {
    Write-Host "Starte APM-System..." -ForegroundColor Yellow
    
    kubectl scale deployment apm-multi-agent --replicas=1 -n $Namespace
    
    # Warten bis System bereit ist
    $maxAttempts = 30
    $attempt = 0
    $success = $false
    
    while ($attempt -lt $maxAttempts) {
        $status = kubectl get deployment apm-multi-agent -n $Namespace -o jsonpath='{.status.availableReplicas}'
        
        if ($status -eq "1") {
            $success = $true
            break
        }
        
        $attempt++
        Write-Host "Warte auf System-Start... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
    
    if ($success) {
        Write-Host "✓ System erfolgreich gestartet" -ForegroundColor Green
    } else {
        Write-Host "✗ System-Start fehlgeschlagen" -ForegroundColor Red
        throw "System konnte nicht gestartet werden"
    }
}

# Hauptausführung
try {
    if (-not $SkipConfirmation) {
        $message = "WARNUNG: Diese Operation wird das System herunterfahren und Daten wiederherstellen.`n"
        $message += "Backup-Datum: $BackupDate`n"
        $message += "Memory Bank: $($RestoreMemoryBank.IsPresent)`n"
        $message += "MongoDB: $($RestoreMongoDB.IsPresent)`n"
        $message += "Möchten Sie fortfahren? (j/n)"
        
        $confirm = Read-Host $message
        if ($confirm -ne "j") {
            Write-Host "Wiederherstellung abgebrochen." -ForegroundColor Yellow
            exit
        }
    }
    
    Test-Prerequisites
    Stop-APMSystem
    
    if ($RestoreMemoryBank) {
        Restore-MemoryBank
    }
    
    if ($RestoreMongoDB) {
        Restore-MongoDB
    }
    
    Start-APMSystem
    
    Write-Host "Wiederherstellung abgeschlossen!" -ForegroundColor Green
} catch {
    Write-Host "Fehler bei der Wiederherstellung: $_" -ForegroundColor Red
    exit 1
} 