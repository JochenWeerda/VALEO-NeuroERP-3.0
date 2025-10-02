# ===================================================
# Verbesserter Chargenbericht-Batchprozessor
# ===================================================
# Leistungsfähiger Batchprozessor mit paralleler Verarbeitung
# für die Generierung von Chargenberichten
# ===================================================

# Lade Hilfsfunktionen
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\powershell_compatibility.ps1"

# Banner anzeigen
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Verbesserter Chargenbericht-Batchprozessor" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""

# Parameter definieren
param (
    [string]$FilterTyp = "alle",
    [string]$FilterWert = "",
    [string]$BerichtTyp = "zusammenfassung",
    [string]$ExportFormat = "pdf",
    [string]$OutputPath = "",
    [int]$MaxChargen = 0,
    [int]$MaxParallel = 4,
    [switch]$EmailVersenden = $false,
    [string]$EmailEmpfaenger = "",
    [switch]$DetailedLog = $false,
    [switch]$Silent = $false
)

# Pfade definieren
$rootDir = Split-Path -Parent $scriptPath
$reportGeneratorPath = Join-Path $scriptPath "automated_report_generator.ps1"
$apiEndpoint = "http://localhost:8003/api/v1/chargen"
$outputDir = if ($OutputPath) { $OutputPath } else { Join-Path $rootDir "reports" }
$logDir = Join-Path $rootDir "logs"
$logFile = Join-Path $logDir "batch_processor_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Überprüfe, ob die Verzeichnisse existieren und erstelle sie gegebenenfalls
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Success "Berichtsverzeichnis erstellt: $outputDir"
}

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
    Write-Success "Log-Verzeichnis erstellt: $logDir"
}

# Verfügbare Filtertypen
$verfuegbareFilter = @(
    "alle", 
    "produkt", 
    "status", 
    "datum", 
    "qualitaet",
    "lagerort",
    "lieferant"
)

# Funktionen
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$ToConsole = $true
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # In Logdatei schreiben
    Add-Content -Path $logFile -Value $logEntry
    
    # Auf Konsole ausgeben, wenn gewünscht
    if ($ToConsole -and -not $Silent) {
        $color = switch ($Level) {
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
        
        Write-Host $logEntry -ForegroundColor $color
    }
}

function Get-ChargenListe {
    param (
        [string]$FilterTyp,
        [string]$FilterWert
    )
    
    try {
        # Basisendpunkt
        $endpoint = $apiEndpoint
        
        # Filter hinzufügen, wenn angegeben
        if ($FilterTyp -ne "alle" -and $FilterWert) {
            $queryParam = switch ($FilterTyp) {
                "produkt" { "product=$FilterWert" }
                "status" { "status=$FilterWert" }
                "datum" { "date=$FilterWert" }
                "qualitaet" { "quality=$FilterWert" }
                "lagerort" { "storage=$FilterWert" }
                "lieferant" { "supplier=$FilterWert" }
                default { "" }
            }
            
            if ($queryParam) {
                $endpoint = "$apiEndpoint`?$queryParam"
            }
        }
        
        Write-Log "API-Anfrage an Endpunkt: $endpoint"
        $response = Invoke-RestMethod -Uri $endpoint -Method Get -ContentType "application/json"
        Write-Log "Anzahl gefundener Chargen: $($response.Count)" -Level "INFO"
        return $response
    }
    catch {
        Write-Log "Fehler beim Abrufen der Chargenliste: $($_.Exception.Message)" -Level "ERROR"
        return @()
    }
}

function Process-Charge {
    param (
        [PSObject]$Charge,
        [string]$BerichtTyp,
        [string]$ExportFormat,
        [string]$OutputPath,
        [int]$ThreadId
    )
    
    try {
        if ($DetailedLog) {
            Write-Log "Thread $ThreadId: Verarbeite Charge $($Charge.id)" -ToConsole:$false
        }
        
        # Erstelle die Argumentliste
        $args = "-ChargeId `"$($Charge.id)`" -BerichtTyp `"$BerichtTyp`" -ExportFormat `"$ExportFormat`""
        
        if ($OutputPath) {
            $args += " -OutputPath `"$OutputPath`""
        }
        
        $args += " -Silent"
        
        # Führe den Berichtsgenerator aus
        $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $reportGeneratorPath $args
        
        # Ermittle den Pfad des generierten Berichts
        $reportFileName = "Charge_$(if ($Charge.chargenNummer) {$Charge.chargenNummer} else {$Charge.id})_$BerichtTyp.$ExportFormat"
        $reportPath = Join-Path $OutputPath $reportFileName
        
        if (Test-Path $reportPath) {
            if ($DetailedLog) {
                Write-Log "Thread $ThreadId: Bericht erfolgreich erstellt: $reportPath" -Level "SUCCESS" -ToConsole:$false
            }
            
            return @{
                success = $true
                chargeid = $Charge.id
                chargenNummer = $Charge.chargenNummer
                path = $reportPath
                errorMessage = $null
            }
        }
        else {
            $errorMsg = "Thread $ThreadId: Bericht konnte nicht erstellt werden für Charge $($Charge.id)"
            Write-Log $errorMsg -Level "ERROR" -ToConsole:$false
            
            return @{
                success = $false
                chargeid = $Charge.id
                chargenNummer = $Charge.chargenNummer
                path = $null
                errorMessage = $errorMsg
            }
        }
    }
    catch {
        $errorMsg = "Thread $ThreadId: Fehler bei der Berichtsgenerierung für Charge $($Charge.id): $($_.Exception.Message)"
        Write-Log $errorMsg -Level "ERROR" -ToConsole:$false
        
        return @{
            success = $false
            chargeid = $Charge.id
            chargenNummer = $Charge.chargenNummer
            path = $null
            errorMessage = $errorMsg
        }
    }
}

function Process-Charges-Parallel {
    param (
        [array]$Chargen,
        [string]$BerichtTyp,
        [string]$ExportFormat,
        [string]$OutputPath,
        [int]$MaxParallel
    )
    
    # Initialisiere Ergebnisse
    $results = @{
        erfolgreich = 0
        fehlgeschlagen = 0
        berichte = @()
        fehlerliste = @()
    }
    
    # PowerShell 5+ unterstützt ForEach -Parallel mit -ThrottleLimit, aber wir implementieren
    # unsere eigene Lösung für maximale Kompatibilität
    
    # Erstelle Runspaces
    $runspacePool = [runspacefactory]::CreateRunspacePool(1, $MaxParallel)
    $runspacePool.Open()
    
    $runspaces = @()
    $total = $Chargen.Count
    $processed = 0
    
    Write-Log "Starte parallele Verarbeitung mit $MaxParallel Threads für $total Chargen" -Level "INFO"
    
    # Bereite Powershell-Instanzen für jeden Thread vor
    foreach ($charge in $Chargen) {
        $powershell = [powershell]::Create().AddScript({
            param($Charge, $BerichtTyp, $ExportFormat, $OutputPath, $ThreadId, $ReportGeneratorPath, $DetailedLog)
            
            # In einem Runspace haben wir keinen Zugriff auf die Funktionen des Hauptskripts,
            # daher müssen wir die Process-Charge-Funktion hier inline implementieren
            
            try {
                # Erstelle die Argumentliste
                $args = "-ChargeId `"$($Charge.id)`" -BerichtTyp `"$BerichtTyp`" -ExportFormat `"$ExportFormat`""
                
                if ($OutputPath) {
                    $args += " -OutputPath `"$OutputPath`""
                }
                
                $args += " -Silent"
                
                # Führe den Berichtsgenerator aus
                $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ReportGeneratorPath $args
                
                # Ermittle den Pfad des generierten Berichts
                $reportFileName = "Charge_$(if ($Charge.chargenNummer) {$Charge.chargenNummer} else {$Charge.id})_$BerichtTyp.$ExportFormat"
                $reportPath = Join-Path $OutputPath $reportFileName
                
                if (Test-Path $reportPath) {
                    return @{
                        success = $true
                        chargeid = $Charge.id
                        chargenNummer = $Charge.chargenNummer
                        path = $reportPath
                        errorMessage = $null
                    }
                }
                else {
                    return @{
                        success = $false
                        chargeid = $Charge.id
                        chargenNummer = $Charge.chargenNummer
                        path = $null
                        errorMessage = "Bericht konnte nicht erstellt werden für Charge $($Charge.id)"
                    }
                }
            }
            catch {
                return @{
                    success = $false
                    chargeid = $Charge.id
                    chargenNummer = $Charge.chargenNummer
                    path = $null
                    errorMessage = "Fehler bei der Berichtsgenerierung für Charge $($Charge.id): $($_.Exception.Message)"
                }
            }
        })
        
        # Parameter übergeben
        $powershell.AddArgument($charge)
        $powershell.AddArgument($BerichtTyp)
        $powershell.AddArgument($ExportFormat)
        $powershell.AddArgument($OutputPath)
        $powershell.AddArgument($runspaces.Count + 1)  # Thread-ID
        $powershell.AddArgument($reportGeneratorPath)
        $powershell.AddArgument($DetailedLog)
        
        # Runspace zuweisen
        $powershell.RunspacePool = $runspacePool
        
        # Asynchron starten
        $runspaces += [PSCustomObject]@{
            Powershell = $powershell
            Handle = $powershell.BeginInvoke()
            Charge = $charge
            Completed = $false
        }
    }
    
    # Progress-Bar einrichten, wenn nicht im Silent-Modus
    if (-not $Silent) {
        $progressParams = @{
            Activity = "Verarbeite Chargenberichte"
            Status = "0% abgeschlossen"
            PercentComplete = 0
        }
        Write-Progress @progressParams
    }
    
    # Ergebnisse sammeln, während die Threads laufen
    do {
        foreach ($runspace in $runspaces | Where-Object { -not $_.Completed }) {
            if ($runspace.Handle.IsCompleted) {
                $result = $runspace.Powershell.EndInvoke($runspace.Handle)
                
                if ($result.success) {
                    $results.erfolgreich++
                    $results.berichte += $result.path
                    
                    if (-not $Silent) {
                        Write-Success "Bericht erstellt: $($result.path)"
                    }
                }
                else {
                    $results.fehlgeschlagen++
                    $results.fehlerliste += $result.errorMessage
                    
                    if (-not $Silent) {
                        Write-Error $result.errorMessage
                    }
                }
                
                # Runspace als abgeschlossen markieren
                $runspace.Completed = $true
                
                # Aufräumen
                $runspace.Powershell.Dispose()
                
                # Fortschritt aktualisieren
                $processed++
                
                if (-not $Silent) {
                    $percentComplete = [math]::Min(100, [math]::Round(($processed / $total) * 100))
                    $progressParams.Status = "$percentComplete% abgeschlossen"
                    $progressParams.PercentComplete = $percentComplete
                    Write-Progress @progressParams
                }
            }
        }
        
        # Kurze Pause, um CPU-Last zu reduzieren
        Start-Sleep -Milliseconds 100
        
    } while ($runspaces | Where-Object { -not $_.Completed })
    
    # Progress-Bar beenden
    if (-not $Silent) {
        Write-Progress -Activity "Verarbeite Chargenberichte" -Completed
    }
    
    # Runspace-Pool schließen
    $runspacePool.Close()
    $runspacePool.Dispose()
    
    Write-Log "Parallele Verarbeitung abgeschlossen: $($results.erfolgreich) erfolgreich, $($results.fehlgeschlagen) fehlgeschlagen" -Level "INFO"
    
    return $results
}

function Send-BatchReportEmail {
    param (
        [string]$Recipient,
        [array]$ReportPaths,
        [string]$FilterInfo,
        [array]$Fehler
    )
    
    if (-not $ReportPaths -or $ReportPaths.Count -eq 0) {
        Write-Log "Keine Berichte zum Versenden vorhanden." -Level "WARNING"
        return $false
    }
    
    try {
        # Erstelle das E-Mail-Objekt
        $outlook = New-Object -ComObject Outlook.Application
        $mail = $outlook.CreateItem(0)
        
        # Setze die E-Mail-Eigenschaften
        $mail.To = $Recipient
        $mail.Subject = "Automatisierte Chargenberichte: $FilterInfo"
        
        $body = "Im Anhang finden Sie die automatisch generierten Berichte für die Chargen mit dem Filter: $FilterInfo.`n`n"
        $body += "Anzahl der Berichte: $($ReportPaths.Count)`n"
        $body += "Berichtstyp: $BerichtTyp`n"
        $body += "Format: $ExportFormat`n"
        
        if ($Fehler.Count -gt 0) {
            $body += "`n`nFehler bei der Verarbeitung ($($Fehler.Count)):`n"
            foreach ($fehler in $Fehler) {
                $body += "- $fehler`n"
            }
        }
        
        $body += "`n`nDiese E-Mail wurde automatisch generiert."
        
        $mail.Body = $body
        
        # Füge die Berichte als Anhänge hinzu
        $reportCounter = 0
        foreach ($reportPath in $ReportPaths) {
            if (Test-Path $reportPath) {
                # E-Mail-Größe begrenzen, max 20 Anhänge
                if ($reportCounter -lt 20) {
                    $mail.Attachments.Add($reportPath)
                    $reportCounter++
                }
                else {
                    Write-Log "Maximale Anzahl von Anhängen erreicht (20). Weitere Berichte werden nicht angehängt." -Level "WARNING"
                    $body += "`n`nHinweis: Es wurden nur die ersten 20 Berichte angehängt. Weitere Berichte finden Sie im Ausgabeverzeichnis."
                    $mail.Body = $body
                    break
                }
            }
        }
        
        $mail.Send()
        Write-Log "E-Mail mit $reportCounter Berichten wurde an $Recipient gesendet." -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Fehler beim Senden der E-Mail: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Create-SummaryReport {
    param (
        [array]$Chargen,
        [hashtable]$Results,
        [string]$FilterInfo,
        [string]$OutputPath
    )
    
    $summaryFileName = "ParallelChargenbatchBericht_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
    $summaryPath = Join-Path $OutputPath $summaryFileName
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Zusammenfassung der parallelen Stapelverarbeitung</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        h2 { color: #3498db; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        tr:hover { background-color: #f5f5f5; }
        .success { color: green; }
        .error { color: red; }
        .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .stats { display: flex; gap: 20px; flex-wrap: wrap; }
        .stat-box { flex: 1; min-width: 150px; padding: 15px; background-color: #e9ecef; border-radius: 5px; text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; margin: 10px 0; }
        .performance { margin-top: 20px; padding: 15px; background-color: #e3f2fd; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Zusammenfassung der parallelen Stapelverarbeitung</h1>
    
    <div class="summary">
        <p><strong>Zeitpunkt:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p><strong>Filter:</strong> $FilterInfo</p>
        <p><strong>Berichtstyp:</strong> $BerichtTyp</p>
        <p><strong>Format:</strong> $ExportFormat</p>
        <p><strong>Parallelität:</strong> $MaxParallel Threads</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <div>Erfolgreich</div>
            <div class="stat-value success">$($Results.erfolgreich)</div>
        </div>
        <div class="stat-box">
            <div>Fehlgeschlagen</div>
            <div class="stat-value $(if ($Results.fehlgeschlagen -gt 0) { "error" } else { "success" })">$($Results.fehlgeschlagen)</div>
        </div>
        <div class="stat-box">
            <div>Gesamtanzahl</div>
            <div class="stat-value">$($Chargen.Count)</div>
        </div>
        <div class="stat-box">
            <div>Erfolgsrate</div>
            <div class="stat-value">$(if ($Chargen.Count -gt 0) { [math]::Round(($Results.erfolgreich / $Chargen.Count) * 100) } else { 0 })%</div>
        </div>
    </div>
    
    <div class="performance">
        <p><strong>Leistungsstatistik:</strong></p>
        <p>Berichte pro Minute: <strong>$(if ($processingTime.TotalMinutes -gt 0) { [math]::Round($Results.erfolgreich / $processingTime.TotalMinutes, 2) } else { "N/A" })</strong></p>
        <p>Gesamtdauer: <strong>$([math]::Round($processingTime.TotalMinutes, 2)) Minuten</strong></p>
    </div>
    
    <h2>Verarbeitete Chargen</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Chargennummer</th>
            <th>Artikel</th>
            <th>Status</th>
            <th>Datum</th>
            <th>Bericht</th>
        </tr>
"@

    foreach ($charge in $Chargen) {
        $reportFileName = "Charge_$(if ($charge.chargenNummer) {$charge.chargenNummer} else {$charge.id})_$BerichtTyp.$ExportFormat"
        $reportPath = Join-Path $OutputPath $reportFileName
        $success = Test-Path $reportPath
        
        $html += @"
        <tr>
            <td>$($charge.id)</td>
            <td>$($charge.chargenNummer)</td>
            <td>$($charge.artikelBezeichnung)</td>
            <td>$($charge.status)</td>
            <td>$($charge.erstellungsDatum)</td>
            <td>$(if ($success) { "<span class='success'>Erstellt</span>" } else { "<span class='error'>Fehlgeschlagen</span>" })</td>
        </tr>
"@
    }

    $html += @"
    </table>
    
    <h2>Generierte Berichte (Erfolgreiche: $($Results.erfolgreich))</h2>
    <ul>
"@

    foreach ($bericht in $Results.berichte) {
        $html += @"
        <li>$bericht</li>
"@
    }

    $html += @"
    </ul>
"@

    if ($Results.fehlerliste.Count -gt 0) {
        $html += @"
    <h2>Fehler (Anzahl: $($Results.fehlerliste.Count))</h2>
    <ul class="error">
"@

        foreach ($fehler in $Results.fehlerliste) {
            $html += @"
        <li>$fehler</li>
"@
        }

        $html += @"
    </ul>
"@
    }

    $html += @"
</body>
</html>
"@

    Set-Content -Path $summaryPath -Value $html
    
    Write-Log "Zusammenfassung erstellt: $summaryPath" -Level "SUCCESS"
    
    return $summaryPath
}

# Starte Timer für Leistungsmessung
$startTime = Get-Date

# Hauptlogik
Write-Log "Verbesserter Chargenbericht-Batchprozessor gestartet" -Level "INFO"
Write-Log "Filter: $FilterTyp=$FilterWert, Berichtstyp: $BerichtTyp, Format: $ExportFormat" -Level "INFO"
Write-Log "Parallele Verarbeitung mit max. $MaxParallel Threads" -Level "INFO"

# Überprüfe, ob der Filtertyp gültig ist
if (-not $verfuegbareFilter.Contains($FilterTyp.ToLower())) {
    Write-Log "Ungültiger Filtertyp: $FilterTyp. Verfügbar sind: $($verfuegbareFilter -join ', ')" -Level "ERROR"
    exit 1
}

# Überprüfe den Report Generator
if (-not (Test-Path $reportGeneratorPath)) {
    Write-Log "Berichtsgenerator nicht gefunden: $reportGeneratorPath" -Level "ERROR"
    exit 1
}

# Hole die Chargenliste
$chargen = Get-ChargenListe -FilterTyp $FilterTyp.ToLower() -FilterWert $FilterWert

if ($chargen.Count -eq 0) {
    Write-Log "Keine Chargen gefunden, die dem Filter entsprechen." -Level "WARNING"
    exit 0
}

Write-Log "Gefundene Chargen: $($chargen.Count)" -Level "INFO"

# Wenn eine maximale Anzahl angegeben wurde, begrenze die Liste
if ($MaxChargen -gt 0 -and $chargen.Count -gt $MaxChargen) {
    $chargen = $chargen | Select-Object -First $MaxChargen
    Write-Log "Verarbeitung begrenzt auf $MaxChargen Chargen" -Level "INFO"
}

# Erstelle eine lesbare Filterbeschreibung
$filterInfo = switch ($FilterTyp.ToLower()) {
    "alle" { "Alle Chargen" }
    "produkt" { "Produkt: $FilterWert" }
    "status" { "Status: $FilterWert" }
    "datum" { "Datum: $FilterWert" }
    "qualitaet" { "Qualität: $FilterWert" }
    "lagerort" { "Lagerort: $FilterWert" }
    "lieferant" { "Lieferant: $FilterWert" }
    default { "Benutzerdefinierter Filter" }
}

# Verarbeite die Chargen parallel
$results = Process-Charges-Parallel `
    -Chargen $chargen `
    -BerichtTyp $BerichtTyp.ToLower() `
    -ExportFormat $ExportFormat.ToLower() `
    -OutputPath $outputDir `
    -MaxParallel $MaxParallel

# Zeitmessung beenden
$endTime = Get-Date
$processingTime = $endTime - $startTime

# Verarbeitungsstatistiken ausgeben
$chargesPerMinute = if ($processingTime.TotalMinutes -gt 0) { 
    [math]::Round($results.erfolgreich / $processingTime.TotalMinutes, 2) 
} else { 
    "N/A" 
}

Write-Log "Verarbeitung abgeschlossen in $([math]::Round($processingTime.TotalMinutes, 2)) Minuten" -Level "INFO"
Write-Log "Leistung: $chargesPerMinute Berichte pro Minute" -Level "INFO"
Write-Log "Erfolgsrate: $(if ($chargen.Count -gt 0) { [math]::Round(($results.erfolgreich / $chargen.Count) * 100) } else { 0 })%" -Level "INFO"

# Erstelle einen Zusammenfassungsbericht
$summaryPath = Create-SummaryReport `
    -Chargen $chargen `
    -Results $results `
    -FilterInfo $filterInfo `
    -OutputPath $outputDir

# Sende E-Mail, wenn gewünscht
if ($EmailVersenden -and $EmailEmpfaenger) {
    # Füge den Zusammenfassungsbericht zu den E-Mail-Anhängen hinzu
    $allReports = $results.berichte + @($summaryPath)
    
    Send-BatchReportEmail `
        -Recipient $EmailEmpfaenger `
        -ReportPaths $allReports `
        -FilterInfo $filterInfo `
        -Fehler $results.fehlerliste
}

# Abschlussnachricht
if (-not $Silent) {
    Write-Host ""
    Write-Success "Stapelverarbeitung abgeschlossen:"
    Write-Host "  Erfolgreich: $($results.erfolgreich)" -ForegroundColor Green
    Write-Host "  Fehlgeschlagen: $($results.fehlgeschlagen)" -ForegroundColor $(if ($results.fehlgeschlagen -gt 0) { "Red" } else { "Green" })
    Write-Host "  Gesamtdauer: $([math]::Round($processingTime.TotalMinutes, 2)) Minuten" -ForegroundColor Cyan
    Write-Host "  Leistung: $chargesPerMinute Berichte/Minute" -ForegroundColor Cyan
    Write-Host "  Zusammenfassung: $summaryPath" -ForegroundColor Cyan
    
    # Öffne den Zusammenfassungsbericht
    try {
        Invoke-Item $summaryPath
    }
    catch {
        Write-Warning "Zusammenfassung konnte nicht automatisch geöffnet werden: $($_.Exception.Message)"
    }
}

Write-Log "Skript beendet mit Statuscode 0" -Level "INFO"
exit 0 