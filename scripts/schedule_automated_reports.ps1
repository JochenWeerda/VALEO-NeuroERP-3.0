# ===================================================
# Scheduler für automatisierte Chargenberichte
# ===================================================
# Ermöglicht die Planung und regelmäßige Ausführung 
# von automatisierten Chargenberichten
# ===================================================

# Lade Hilfsfunktionen
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\powershell_compatibility.ps1"

# Banner anzeigen
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Scheduler für automatisierte Chargenberichte" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""

# Parameter definieren
param (
    [string]$ConfigFile = "",
    [string]$ChargeId = "",
    [string]$BerichtTyp = "zusammenfassung",
    [string]$ExportFormat = "pdf",
    [string]$OutputPath = "",
    [string]$Schedule = "täglich",
    [string]$Zeit = "08:00",
    [string]$EmailEmpfaenger = "",
    [switch]$List = $false,
    [switch]$Remove = $false,
    [int]$RemoveId = -1
)

# Pfade definieren
$rootDir = Split-Path -Parent $scriptPath
$defaultConfigFile = Join-Path $rootDir "config\report_schedule.json"
$reportGeneratorPath = Join-Path $scriptPath "automated_report_generator.ps1"

# Überprüfe, ob der Konfigurationspfad existiert
$configDir = Join-Path $rootDir "config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
    Write-Success "Konfigurationsverzeichnis erstellt: $configDir"
}

# Konfigurationsdatei festlegen
$configFile = if ($ConfigFile) { $ConfigFile } else { $defaultConfigFile }

# Funktionen
function Initialize-ConfigFile {
    param (
        [string]$ConfigFile
    )
    
    if (-not (Test-Path $ConfigFile)) {
        $initialConfig = @{
            schedules = @()
        }
        
        $initialConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigFile
        Write-Success "Neue Konfigurationsdatei erstellt: $ConfigFile"
    }
}

function Get-Schedules {
    param (
        [string]$ConfigFile
    )
    
    if (Test-Path $ConfigFile) {
        $config = Get-Content -Path $ConfigFile -Raw | ConvertFrom-Json
        return $config.schedules
    }
    
    return @()
}

function Add-Schedule {
    param (
        [string]$ConfigFile,
        [string]$ChargeId,
        [string]$BerichtTyp,
        [string]$ExportFormat,
        [string]$OutputPath,
        [string]$Schedule,
        [string]$Zeit,
        [string]$EmailEmpfaenger
    )
    
    # Lade die aktuelle Konfiguration
    $config = Get-Content -Path $ConfigFile -Raw | ConvertFrom-Json
    
    # Erstelle eine neue ID
    $newId = 1
    if ($config.schedules.Count -gt 0) {
        $newId = ($config.schedules | Measure-Object -Property id -Maximum).Maximum + 1
    }
    
    # Erstelle einen neuen Zeitplan
    $newSchedule = [PSCustomObject]@{
        id = $newId
        chargeId = $ChargeId
        berichtTyp = $BerichtTyp
        exportFormat = $ExportFormat
        outputPath = $OutputPath
        schedule = $Schedule
        zeit = $Zeit
        emailEmpfaenger = $EmailEmpfaenger
        erstelltAm = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        letzteAusfuehrung = $null
        aktiv = $true
    }
    
    # Füge den neuen Zeitplan hinzu
    $config.schedules += $newSchedule
    
    # Speichere die aktualisierte Konfiguration
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigFile
    
    return $newSchedule
}

function Remove-Schedule {
    param (
        [string]$ConfigFile,
        [int]$Id
    )
    
    # Lade die aktuelle Konfiguration
    $config = Get-Content -Path $ConfigFile -Raw | ConvertFrom-Json
    
    # Suche den Zeitplan mit der angegebenen ID
    $scheduleIndex = -1
    for ($i = 0; $i -lt $config.schedules.Count; $i++) {
        if ($config.schedules[$i].id -eq $Id) {
            $scheduleIndex = $i
            break
        }
    }
    
    if ($scheduleIndex -ge 0) {
        # Entferne den Zeitplan
        $removedSchedule = $config.schedules[$scheduleIndex]
        $config.schedules = @($config.schedules | Where-Object { $_.id -ne $Id })
        
        # Speichere die aktualisierte Konfiguration
        $config | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigFile
        
        return $removedSchedule
    }
    
    return $null
}

function Display-Schedules {
    param (
        [array]$Schedules
    )
    
    Write-Host "Geplante Berichte:" -ForegroundColor Green
    Write-Host "------------------------------------------------------------" -ForegroundColor Green
    
    if ($Schedules.Count -eq 0) {
        Write-Host "  Keine geplanten Berichte vorhanden." -ForegroundColor Yellow
        return
    }
    
    foreach ($schedule in $Schedules) {
        Write-Host "ID: $($schedule.id)" -ForegroundColor Cyan
        Write-Host "  Charge: $($schedule.chargeId)"
        Write-Host "  Berichtstyp: $($schedule.berichtTyp)"
        Write-Host "  Format: $($schedule.exportFormat)"
        Write-Host "  Zeitplan: $($schedule.schedule) um $($schedule.zeit)"
        
        if ($schedule.emailEmpfaenger) {
            Write-Host "  E-Mail-Empfänger: $($schedule.emailEmpfaenger)"
        }
        
        if ($schedule.letzteAusfuehrung) {
            Write-Host "  Letzte Ausführung: $($schedule.letzteAusfuehrung)"
        }
        
        Write-Host "  Status: $(if ($schedule.aktiv) { 'Aktiv' } else { 'Inaktiv' })"
        Write-Host "------------------------------------------------------------" -ForegroundColor Green
    }
}

function Create-ScheduledTask {
    param (
        [string]$TaskName,
        [string]$ScriptPath,
        [string]$Arguments,
        [string]$TriggerTime,
        [string]$Schedule
    )
    
    # Erstelle den PowerShell-Befehl
    $action = "-File `"$ScriptPath`" $Arguments -Scheduled"
    
    # Konvertiere den Zeitplan in einen Trigger
    $trigger = switch ($Schedule.ToLower()) {
        "täglich" { "Daily" }
        "wöchentlich" { "Weekly" }
        "monatlich" { "Monthly" }
        "stündlich" { "Hourly" }
        default { "Daily" }
    }
    
    # Erstelle den Zeitplantyp
    $frequency = switch ($Schedule.ToLower()) {
        "täglich" { "Daily" }
        "wöchentlich" { "Weekly" }
        "monatlich" { "Monthly" }
        "stündlich" { "Hourly" }
        default { "Daily" }
    }
    
    # Extrahiere Stunde und Minute aus der Zeit
    $hour = [int]($TriggerTime.Split(':')[0])
    $minute = [int]($TriggerTime.Split(':')[1])
    
    try {
        # Erstelle das Scheduler-Objekt
        $sched = New-Object -ComObject Schedule.Service
        $sched.Connect()
        
        # Erstelle die Task-Definition
        $task = $sched.NewTask(0)
        
        # Erstelle den Trigger
        $triggers = $task.Triggers
        $newTrigger = $triggers.Create(2) # 2 = Daily
        $newTrigger.StartBoundary = [DateTime]::Today.AddHours($hour).AddMinutes($minute).ToString("yyyy-MM-ddTHH:mm:ss")
        $newTrigger.Enabled = $true
        
        if ($frequency -eq "Weekly") {
            $newTrigger.DaysOfWeek = 0x7F # Alle Tage der Woche
        }
        elseif ($frequency -eq "Monthly") {
            $newTrigger.MonthsOfYear = 0xFFF # Alle Monate
            $newTrigger.DaysOfMonth = 0x7FFFFFFF # Alle Tage des Monats
        }
        elseif ($frequency -eq "Hourly") {
            $newTrigger.Repetition.Interval = "PT1H" # PT1H = 1 Stunde
            $newTrigger.Repetition.Duration = "P1D" # P1D = 1 Tag
        }
        
        # Erstelle die Aktion
        $actions = $task.Actions
        $action = $actions.Create(0) # 0 = Execute
        $action.Path = "powershell.exe"
        $action.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`" $Arguments -Scheduled"
        
        # Setze weitere Task-Eigenschaften
        $task.Settings.Enabled = $true
        $task.Settings.Hidden = $false
        
        # Registriere die Task
        $taskFolder = $sched.GetFolder("\")
        $taskFolder.RegisterTaskDefinition($TaskName, $task, 6, $null, $null, 3) # 6 = Create or update, 3 = Run whether user is logged on or not
        
        Write-Success "Aufgabe '$TaskName' wurde erfolgreich geplant."
        return $true
    }
    catch {
        Write-Error "Fehler beim Erstellen der geplanten Aufgabe: $($_.Exception.Message)"
        return $false
    }
}

function Send-ReportEmail {
    param (
        [string]$Recipient,
        [string]$ReportPath,
        [string]$ChargeId,
        [string]$BerichtTyp
    )
    
    try {
        # Erstelle das E-Mail-Objekt
        $outlook = New-Object -ComObject Outlook.Application
        $mail = $outlook.CreateItem(0)
        
        # Setze die E-Mail-Eigenschaften
        $mail.To = $Recipient
        $mail.Subject = "Automatisierter Chargenbericht: $ChargeId - $BerichtTyp"
        $mail.Body = "Im Anhang finden Sie den automatisch generierten Bericht für Charge $ChargeId.`n`nDiese E-Mail wurde automatisch generiert."
        
        # Füge den Bericht als Anhang hinzu
        if (Test-Path $ReportPath) {
            $mail.Attachments.Add($ReportPath)
            $mail.Send()
            Write-Success "E-Mail mit Bericht wurde an $Recipient gesendet."
            return $true
        }
        else {
            Write-Error "Die Berichtsdatei existiert nicht: $ReportPath"
            return $false
        }
    }
    catch {
        Write-Error "Fehler beim Senden der E-Mail: $($_.Exception.Message)"
        return $false
    }
}

function Run-ScheduledReport {
    param (
        [PSObject]$Schedule,
        [string]$ReportGeneratorPath
    )
    
    # Erstelle die Argumentliste
    $args = "-ChargeId `"$($Schedule.chargeId)`" -BerichtTyp `"$($Schedule.berichtTyp)`" -ExportFormat `"$($Schedule.exportFormat)`""
    
    if ($Schedule.outputPath) {
        $args += " -OutputPath `"$($Schedule.outputPath)`""
    }
    
    $args += " -Silent"
    
    try {
        # Führe den Berichtsgenerator aus
        $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ReportGeneratorPath $args
        
        # Aktualisiere die letzte Ausführungszeit
        Update-LastExecutionTime -ConfigFile $configFile -Id $Schedule.id
        
        # Sende den Bericht per E-Mail, wenn ein Empfänger angegeben wurde
        if ($Schedule.emailEmpfaenger) {
            $reportFileName = "Charge_$($Schedule.chargeId)_$($Schedule.berichtTyp).$($Schedule.exportFormat)"
            $reportPath = if ($Schedule.outputPath) { 
                Join-Path $Schedule.outputPath $reportFileName 
            } else { 
                Join-Path (Join-Path $rootDir "reports") $reportFileName 
            }
            
            Send-ReportEmail -Recipient $Schedule.emailEmpfaenger -ReportPath $reportPath -ChargeId $Schedule.chargeId -BerichtTyp $Schedule.berichtTyp
        }
        
        return $true
    }
    catch {
        Write-Error "Fehler bei der Ausführung des geplanten Berichts: $($_.Exception.Message)"
        return $false
    }
}

function Update-LastExecutionTime {
    param (
        [string]$ConfigFile,
        [int]$Id
    )
    
    # Lade die aktuelle Konfiguration
    $config = Get-Content -Path $ConfigFile -Raw | ConvertFrom-Json
    
    # Suche den Zeitplan mit der angegebenen ID
    for ($i = 0; $i -lt $config.schedules.Count; $i++) {
        if ($config.schedules[$i].id -eq $Id) {
            $config.schedules[$i].letzteAusfuehrung = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            break
        }
    }
    
    # Speichere die aktualisierte Konfiguration
    $config | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigFile
}

# Hauptlogik
# Überprüfe, ob die Konfigurationsdatei existiert, und erstelle sie gegebenenfalls
Initialize-ConfigFile -ConfigFile $configFile

# Liste alle geplanten Berichte auf, wenn der Parameter -List angegeben wurde
if ($List) {
    $schedules = Get-Schedules -ConfigFile $configFile
    Display-Schedules -Schedules $schedules
    exit 0
}

# Entferne einen geplanten Bericht, wenn der Parameter -Remove angegeben wurde
if ($Remove) {
    if ($RemoveId -lt 0) {
        Write-Error "Keine gültige ID zum Entfernen angegeben. Verwende -RemoveId <ID>."
        exit 1
    }
    
    $removedSchedule = Remove-Schedule -ConfigFile $configFile -Id $RemoveId
    
    if ($removedSchedule) {
        Write-Success "Zeitplan mit ID $RemoveId wurde erfolgreich entfernt."
        
        # Entferne auch die geplante Aufgabe
        $taskName = "ChargeBericht_$($removedSchedule.id)"
        try {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
            Write-Success "Geplante Aufgabe '$taskName' wurde entfernt."
        }
        catch {
            Write-Warning "Geplante Aufgabe konnte nicht entfernt werden: $($_.Exception.Message)"
        }
    }
    else {
        Write-Error "Zeitplan mit ID $RemoveId nicht gefunden."
    }
    
    exit 0
}

# Prüfe, ob ein Charge-ID angegeben wurde
if (-not $ChargeId) {
    Write-Error "Keine Charge-ID angegeben. Verwende den Parameter -ChargeId."
    exit 1
}

# Überprüfe den Report Generator
if (-not (Test-Path $reportGeneratorPath)) {
    Write-Error "Berichtsgenerator nicht gefunden: $reportGeneratorPath"
    exit 1
}

# Erstelle einen neuen Zeitplan
$newSchedule = Add-Schedule `
    -ConfigFile $configFile `
    -ChargeId $ChargeId `
    -BerichtTyp $BerichtTyp `
    -ExportFormat $ExportFormat `
    -OutputPath $OutputPath `
    -Schedule $Schedule `
    -Zeit $Zeit `
    -EmailEmpfaenger $EmailEmpfaenger

if ($newSchedule) {
    Write-Success "Neuer Zeitplan erstellt mit ID: $($newSchedule.id)"
    
    # Erstelle die Argumentliste für die geplante Aufgabe
    $taskArgs = "-ChargeId `"$ChargeId`" -BerichtTyp `"$BerichtTyp`" -ExportFormat `"$ExportFormat`""
    
    if ($OutputPath) {
        $taskArgs += " -OutputPath `"$OutputPath`""
    }
    
    if ($EmailEmpfaenger) {
        $taskArgs += " -EmailEmpfaenger `"$EmailEmpfaenger`""
    }
    
    $taskArgs += " -Silent"
    
    # Erstelle die geplante Aufgabe
    $taskName = "ChargeBericht_$($newSchedule.id)"
    Create-ScheduledTask `
        -TaskName $taskName `
        -ScriptPath $reportGeneratorPath `
        -Arguments $taskArgs `
        -TriggerTime $Zeit `
        -Schedule $Schedule
    
    # Teste den Bericht sofort aus
    Write-Info "Führe den Bericht einmalig aus, um die Konfiguration zu testen..."
    Run-ScheduledReport -Schedule $newSchedule -ReportGeneratorPath $reportGeneratorPath
}
else {
    Write-Error "Fehler beim Erstellen des Zeitplans."
    exit 1
}

exit 0 