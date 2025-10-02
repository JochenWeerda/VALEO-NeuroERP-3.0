# Mode Switch Script für VALEO-NeuroERP
# Dieses Skript ermöglicht das Wechseln zwischen verschiedenen Modi (VAN, PLAN, CREATIVE, IMPLEMENT, REFLECT, ARCHIVE)

param(
    [Parameter(Mandatory=$false)]
    [string]$Mode = "",

    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# Farbdefinitionen für die Ausgabe
$colorVAN = "Cyan"
$colorPLAN = "Yellow"
$colorCREATIVE = "Magenta"
$colorIMPLEMENT = "Green"
$colorREFLECT = "Blue"
$colorARCHIVE = "DarkGray"
$colorError = "Red"
$colorSuccess = "Green"

# Pfade zu den Regeldateien
$rulesPath = ".cursor/rules"
$vanRulesPath = "$rulesPath/van_mode_rules.json"
$planRulesPath = "$rulesPath/plan_mode_rules.json"
$creativeRulesPath = "$rulesPath/creative_mode_rules.json"
$implementRulesPath = "$rulesPath/implement_mode_rules.json"
$reflectArchiveRulesPath = "$rulesPath/reflect_archive_rules.json"

# Pfade zu den Memory-Bank-Verzeichnissen
$memoryBankPath = "memory-bank"
$validationPath = "$memoryBankPath/validation"
$planningPath = "$memoryBankPath/planning"
$creativePath = "$memoryBankPath/creative"
$reflectionPath = "$memoryBankPath/reflection"
$archivePath = "$memoryBankPath/archive"
$handoverPath = "$memoryBankPath/handover"
$activeContextPath = "$memoryBankPath/activeContext.md"

# Funktion zum Anzeigen der Hilfe
function Show-Help {
    Write-Host "Mode Switch Script für VALEO-NeuroERP" -ForegroundColor White
    Write-Host "Verwendung: .\mode_switch.ps1 -Mode <Modus>" -ForegroundColor White
    Write-Host ""
    Write-Host "Verfügbare Modi:" -ForegroundColor White
    Write-Host "  VAN       - Validieren und Analysieren" -ForegroundColor $colorVAN
    Write-Host "  PLAN      - Planen der Implementierung" -ForegroundColor $colorPLAN
    Write-Host "  CREATIVE  - Kreative Phase für Design-Entscheidungen" -ForegroundColor $colorCREATIVE
    Write-Host "  IMPLEMENT - Implementierung gemäß Plan" -ForegroundColor $colorIMPLEMENT
    Write-Host "  REFLECT   - Reflexion über die Implementierung" -ForegroundColor $colorREFLECT
    Write-Host "  ARCHIVE   - Archivierung der abgeschlossenen Aufgabe" -ForegroundColor $colorARCHIVE
    Write-Host ""
    Write-Host "Beispiel: .\mode_switch.ps1 -Mode VAN" -ForegroundColor White
    Write-Host ""
}

# Funktion zur Überprüfung, ob die Regeldateien existieren
function Test-RulesExist {
    $allRulesExist = $true

    if (-not (Test-Path $vanRulesPath)) {
        Write-Host "Fehler: VAN-Modus-Regeln nicht gefunden in $vanRulesPath" -ForegroundColor $colorError
        $allRulesExist = $false
    }

    if (-not (Test-Path $planRulesPath)) {
        Write-Host "Fehler: PLAN-Modus-Regeln nicht gefunden in $planRulesPath" -ForegroundColor $colorError
        $allRulesExist = $false
    }

    if (-not (Test-Path $creativeRulesPath)) {
        Write-Host "Fehler: CREATIVE-Modus-Regeln nicht gefunden in $creativeRulesPath" -ForegroundColor $colorError
        $allRulesExist = $false
    }

    if (-not (Test-Path $implementRulesPath)) {
        Write-Host "Fehler: IMPLEMENT-Modus-Regeln nicht gefunden in $implementRulesPath" -ForegroundColor $colorError
        $allRulesExist = $false
    }

    if (-not (Test-Path $reflectArchiveRulesPath)) {
        Write-Host "Fehler: REFLECT-ARCHIVE-Modus-Regeln nicht gefunden in $reflectArchiveRulesPath" -ForegroundColor $colorError
        $allRulesExist = $false
    }

    return $allRulesExist
}

# Funktion zur Überprüfung, ob die Memory-Bank-Verzeichnisse existieren
function Test-MemoryBankExists {
    $allDirectoriesExist = $true

    if (-not (Test-Path $memoryBankPath)) {
        Write-Host "Fehler: Memory-Bank-Verzeichnis nicht gefunden in $memoryBankPath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    if (-not (Test-Path $validationPath)) {
        Write-Host "Fehler: Validierungs-Verzeichnis nicht gefunden in $validationPath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    if (-not (Test-Path $planningPath)) {
        Write-Host "Fehler: Planungs-Verzeichnis nicht gefunden in $planningPath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    if (-not (Test-Path $creativePath)) {
        Write-Host "Fehler: Creative-Verzeichnis nicht gefunden in $creativePath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    if (-not (Test-Path $reflectionPath)) {
        Write-Host "Fehler: Reflexions-Verzeichnis nicht gefunden in $reflectionPath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    if (-not (Test-Path $archivePath)) {
        Write-Host "Fehler: Archiv-Verzeichnis nicht gefunden in $archivePath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    if (-not (Test-Path $handoverPath)) {
        Write-Host "Fehler: Handover-Verzeichnis nicht gefunden in $handoverPath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    if (-not (Test-Path $activeContextPath)) {
        Write-Host "Fehler: Active-Context-Datei nicht gefunden in $activeContextPath" -ForegroundColor $colorError
        $allDirectoriesExist = $false
    }

    return $allDirectoriesExist
}

# Funktion zum Erstellen eines Handover-Dokuments
function New-HandoverDocument {
    param(
        [string]$FromMode,
        [string]$ToMode
    )

    $handoverTemplate = "$handoverPath/handover-template.md"
    $lastHandover = "$handoverPath/last-handover.md"
    $handoverHistory = "$handoverPath/handover-history"
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $historyHandover = "$handoverHistory/handover_${FromMode}_to_${ToMode}_$timestamp.md"

    # Erstelle das Handover-Verzeichnis für die Historie, falls es nicht existiert
    if (-not (Test-Path $handoverHistory)) {
        New-Item -ItemType Directory -Path $handoverHistory -Force | Out-Null
    }

    # Kopiere das letzte Handover in die Historie, falls es existiert
    if (Test-Path $lastHandover) {
        Copy-Item $lastHandover $historyHandover
    }

    # Erstelle ein neues Handover-Dokument basierend auf der Vorlage
    if (Test-Path $handoverTemplate) {
        $content = Get-Content $handoverTemplate -Raw
        $content = $content -replace "\[Datum\]", (Get-Date -Format "dd.MM.yyyy")
        $content = $content -replace "\[Aktuelle Aufgabe\]", "Moduswechsel von $FromMode zu $ToMode"
        $content = $content -replace "\[Aktuelle Modus\]", $ToMode
        $content = $content -replace "\[Übergeben von\]", "Mode Switch Script"
        $content = $content -replace "\[Übergeben an\]", "Nächster Agent"
        $content = $content -replace "\[Datum und Uhrzeit\]", (Get-Date -Format "dd.MM.yyyy, HH:mm")
        
        $content | Out-File $lastHandover -Encoding utf8
        Write-Host "Handover-Dokument erstellt: $lastHandover" -ForegroundColor $colorSuccess
    } else {
        Write-Host "Warnung: Handover-Vorlage nicht gefunden in $handoverTemplate" -ForegroundColor "Yellow"
    }
}

# Funktion zum Aktualisieren des aktiven Kontexts
function Update-ActiveContext {
    param(
        [string]$Mode
    )

    if (Test-Path $activeContextPath) {
        $content = Get-Content $activeContextPath -Raw
        $timestamp = Get-Date -Format "dd.MM.yyyy HH:mm"
        
        # Füge den Moduswechsel am Ende der Datei hinzu
        $newContent = $content + "`n`n## Moduswechsel zu $Mode`n`nDatum: $timestamp`n`nDer Modus wurde zu $Mode gewechselt. Alle Aktionen sollten nun gemäß den Regeln des $Mode-Modus durchgeführt werden."
        
        $newContent | Out-File $activeContextPath -Encoding utf8
        Write-Host "Aktiver Kontext aktualisiert in $activeContextPath" -ForegroundColor $colorSuccess
    } else {
        Write-Host "Fehler: Active-Context-Datei nicht gefunden in $activeContextPath" -ForegroundColor $colorError
    }
}

# Hauptfunktion zum Wechseln des Modus
function Switch-Mode {
    param(
        [string]$Mode
    )

    # Überprüfe, ob die Regeldateien und Memory-Bank-Verzeichnisse existieren
    $rulesExist = Test-RulesExist
    $memoryBankExists = Test-MemoryBankExists

    if (-not $rulesExist -or -not $memoryBankExists) {
        Write-Host "Fehler: Modus kann nicht gewechselt werden, da erforderliche Dateien oder Verzeichnisse fehlen." -ForegroundColor $colorError
        return
    }

    # Bestimme den aktuellen Modus (falls möglich)
    $currentMode = "UNKNOWN"
    if (Test-Path "$memoryBankPath/current_mode.txt") {
        $currentMode = Get-Content "$memoryBankPath/current_mode.txt"
    }

    # Wechsle den Modus basierend auf der Eingabe
    switch ($Mode.ToUpper()) {
        "VAN" {
            Write-Host "Wechsle zum VAN-Modus (Validieren und Analysieren)" -ForegroundColor $colorVAN
            "VAN" | Out-File "$memoryBankPath/current_mode.txt" -Encoding utf8
            New-HandoverDocument -FromMode $currentMode -ToMode "VAN"
            Update-ActiveContext -Mode "VAN"
            
            # Hier könnten weitere Aktionen für den VAN-Modus hinzugefügt werden
            # z.B. Ausführen von Validierungsskripten
            
            Write-Host "VAN-Modus aktiviert. Validiere und analysiere das System gemäß den VAN-Modus-Regeln." -ForegroundColor $colorVAN
        }
        "PLAN" {
            Write-Host "Wechsle zum PLAN-Modus" -ForegroundColor $colorPLAN
            "PLAN" | Out-File "$memoryBankPath/current_mode.txt" -Encoding utf8
            New-HandoverDocument -FromMode $currentMode -ToMode "PLAN"
            Update-ActiveContext -Mode "PLAN"
            
            Write-Host "PLAN-Modus aktiviert. Erstelle einen strukturierten Implementierungsplan gemäß den PLAN-Modus-Regeln." -ForegroundColor $colorPLAN
        }
        "CREATIVE" {
            Write-Host "Wechsle zum CREATIVE-Modus" -ForegroundColor $colorCREATIVE
            "CREATIVE" | Out-File "$memoryBankPath/current_mode.txt" -Encoding utf8
            New-HandoverDocument -FromMode $currentMode -ToMode "CREATIVE"
            Update-ActiveContext -Mode "CREATIVE"
            
            Write-Host "CREATIVE-Modus aktiviert. Generiere und bewerte multiple Design-Optionen gemäß den CREATIVE-Modus-Regeln." -ForegroundColor $colorCREATIVE
        }
        "IMPLEMENT" {
            Write-Host "Wechsle zum IMPLEMENT-Modus" -ForegroundColor $colorIMPLEMENT
            "IMPLEMENT" | Out-File "$memoryBankPath/current_mode.txt" -Encoding utf8
            New-HandoverDocument -FromMode $currentMode -ToMode "IMPLEMENT"
            Update-ActiveContext -Mode "IMPLEMENT"
            
            Write-Host "IMPLEMENT-Modus aktiviert. Implementiere Änderungen gemäß dem Plan und den IMPLEMENT-Modus-Regeln." -ForegroundColor $colorIMPLEMENT
        }
        "REFLECT" {
            Write-Host "Wechsle zum REFLECT-Modus" -ForegroundColor $colorREFLECT
            "REFLECT" | Out-File "$memoryBankPath/current_mode.txt" -Encoding utf8
            New-HandoverDocument -FromMode $currentMode -ToMode "REFLECT"
            Update-ActiveContext -Mode "REFLECT"
            
            Write-Host "REFLECT-Modus aktiviert. Reflektiere über die Implementierung gemäß den REFLECT-ARCHIVE-Modus-Regeln." -ForegroundColor $colorREFLECT
        }
        "ARCHIVE" {
            Write-Host "Wechsle zum ARCHIVE-Modus" -ForegroundColor $colorARCHIVE
            "ARCHIVE" | Out-File "$memoryBankPath/current_mode.txt" -Encoding utf8
            New-HandoverDocument -FromMode $currentMode -ToMode "ARCHIVE"
            Update-ActiveContext -Mode "ARCHIVE"
            
            Write-Host "ARCHIVE-Modus aktiviert. Archiviere die abgeschlossene Aufgabe gemäß den REFLECT-ARCHIVE-Modus-Regeln." -ForegroundColor $colorARCHIVE
        }
        default {
            Write-Host "Fehler: Ungültiger Modus '$Mode'" -ForegroundColor $colorError
            Write-Host "Gültige Modi sind: VAN, PLAN, CREATIVE, IMPLEMENT, REFLECT, ARCHIVE" -ForegroundColor $colorError
            Show-Help
            return
        }
    }
}

# Hauptlogik des Skripts
if ($Help) {
    Show-Help
} elseif ($Mode -eq "") {
    # Wenn kein Modus angegeben wurde, zeige den aktuellen Modus an
    if (Test-Path "$memoryBankPath/current_mode.txt") {
        $currentMode = Get-Content "$memoryBankPath/current_mode.txt"
        Write-Host "Aktueller Modus: $currentMode" -ForegroundColor White
    } else {
        Write-Host "Aktueller Modus: Nicht gesetzt" -ForegroundColor White
    }
    Show-Help
} else {
    # Wechsle zum angegebenen Modus
    Switch-Mode -Mode $Mode
} 
