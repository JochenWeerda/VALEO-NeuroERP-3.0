# ===================================================
# Stapelverarbeitung für Chargenberichte
# ===================================================
# Ermöglicht die Generierung mehrerer Chargenberichte
# auf einmal über verschiedene Filter
# ===================================================

# Lade Hilfsfunktionen
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\powershell_compatibility.ps1"

# Banner anzeigen
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Stapelverarbeitung für Chargenberichte" -ForegroundColor Cyan
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
    [switch]$EmailVersenden = $false,
    [string]$EmailEmpfaenger = "",
    [switch]$Silent = $false
)

# Pfade definieren
$rootDir = Split-Path -Parent $scriptPath
$reportGeneratorPath = Join-Path $scriptPath "automated_report_generator.ps1"
$apiEndpoint = "http://localhost:8003/api/v1/chargen"
$outputDir = if ($OutputPath) { $OutputPath } else { Join-Path $rootDir "reports" }

# Überprüfe, ob der Ausgabepfad existiert
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Success "Berichtsverzeichnis erstellt: $outputDir"
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
        
        $response = Invoke-RestMethod -Uri $endpoint -Method Get -ContentType "application/json"
        return $response
    }
    catch {
        Write-Error "Fehler beim Abrufen der Chargenliste: $($_.Exception.Message)"
        return @()
    }
}

function Generate-BatchReports {
    param (
        [array]$Chargen,
        [string]$BerichtTyp,
        [string]$ExportFormat,
        [string]$OutputPath,
        [int]$MaxChargen = 0
    )
    
    # Wenn eine maximale Anzahl angegeben wurde, begrenze die Liste
    if ($MaxChargen -gt 0 -and $Chargen.Count -gt $MaxChargen) {
        $Chargen = $Chargen | Select-Object -First $MaxChargen
    }
    
    $erfolgreich = 0
    $fehlgeschlagen = 0
    $berichte = @()
    
    foreach ($charge in $Chargen) {
        if (-not $Silent) {
            Write-Info "Generiere Bericht für Charge $($charge.id)..."
        }
        
        # Erstelle die Argumentliste
        $args = "-ChargeId `"$($charge.id)`" -BerichtTyp `"$BerichtTyp`" -ExportFormat `"$ExportFormat`""
        
        if ($OutputPath) {
            $args += " -OutputPath `"$OutputPath`""
        }
        
        $args += " -Silent"
        
        try {
            # Führe den Berichtsgenerator aus
            $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $reportGeneratorPath $args
            
            # Ermittle den Pfad des generierten Berichts
            $reportFileName = "Charge_$(if ($charge.chargenNummer) {$charge.chargenNummer} else {$charge.id})_$BerichtTyp.$ExportFormat"
            $reportPath = Join-Path $OutputPath $reportFileName
            
            if (Test-Path $reportPath) {
                $erfolgreich++
                $berichte += $reportPath
                
                if (-not $Silent) {
                    Write-Success "Bericht erstellt: $reportPath"
                }
            }
            else {
                $fehlgeschlagen++
                Write-Error "Bericht konnte nicht erstellt werden für Charge $($charge.id)"
            }
        }
        catch {
            $fehlgeschlagen++
            Write-Error "Fehler bei der Berichtsgenerierung für Charge $($charge.id): $($_.Exception.Message)"
        }
    }
    
    return @{
        erfolgreich = $erfolgreich
        fehlgeschlagen = $fehlgeschlagen
        berichte = $berichte
    }
}

function Send-BatchReportEmail {
    param (
        [string]$Recipient,
        [array]$ReportPaths,
        [string]$FilterInfo
    )
    
    if (-not $ReportPaths -or $ReportPaths.Count -eq 0) {
        Write-Warning "Keine Berichte zum Versenden vorhanden."
        return $false
    }
    
    try {
        # Erstelle das E-Mail-Objekt
        $outlook = New-Object -ComObject Outlook.Application
        $mail = $outlook.CreateItem(0)
        
        # Setze die E-Mail-Eigenschaften
        $mail.To = $Recipient
        $mail.Subject = "Stapelverarbeitung von Chargenberichten: $FilterInfo"
        
        $body = "Im Anhang finden Sie die automatisch generierten Berichte für die Chargen mit dem Filter: $FilterInfo.`n`n"
        $body += "Anzahl der Berichte: $($ReportPaths.Count)`n"
        $body += "Berichtstyp: $BerichtTyp`n"
        $body += "Format: $ExportFormat`n`n"
        $body += "Diese E-Mail wurde automatisch generiert."
        
        $mail.Body = $body
        
        # Füge die Berichte als Anhänge hinzu
        foreach ($reportPath in $ReportPaths) {
            if (Test-Path $reportPath) {
                $mail.Attachments.Add($reportPath)
            }
        }
        
        $mail.Send()
        Write-Success "E-Mail mit $($ReportPaths.Count) Berichten wurde an $Recipient gesendet."
        return $true
    }
    catch {
        Write-Error "Fehler beim Senden der E-Mail: $($_.Exception.Message)"
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
    
    $summaryFileName = "ChargenbatchBericht_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"
    $summaryPath = Join-Path $OutputPath $summaryFileName
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Zusammenfassung der Stapelverarbeitung</title>
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
    </style>
</head>
<body>
    <h1>Zusammenfassung der Stapelverarbeitung</h1>
    
    <div class="summary">
        <p><strong>Zeitpunkt:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p><strong>Filter:</strong> $FilterInfo</p>
        <p><strong>Berichtstyp:</strong> $BerichtTyp</p>
        <p><strong>Format:</strong> $ExportFormat</p>
        <p><strong>Erfolgreich:</strong> <span class="success">$($Results.erfolgreich)</span></p>
        <p><strong>Fehlgeschlagen:</strong> <span class="error">$($Results.fehlgeschlagen)</span></p>
        <p><strong>Gesamtanzahl:</strong> $($Chargen.Count)</p>
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
    
    <h2>Generierte Berichte</h2>
    <ul>
"@

    foreach ($bericht in $Results.berichte) {
        $html += @"
        <li>$bericht</li>
"@
    }

    $html += @"
    </ul>
</body>
</html>
"@

    Set-Content -Path $summaryPath -Value $html
    
    if (-not $Silent) {
        Write-Success "Zusammenfassung erstellt: $summaryPath"
    }
    
    return $summaryPath
}

# Hauptlogik
if (-not $Silent) {
    Write-Info "Stapelverarbeitung von Chargenberichten gestartet"
}

# Überprüfe, ob der Filtertyp gültig ist
if (-not $verfuegbareFilter.Contains($FilterTyp.ToLower())) {
    Write-Error "Ungültiger Filtertyp: $FilterTyp. Verfügbar sind: $($verfuegbareFilter -join ', ')"
    exit 1
}

# Überprüfe den Report Generator
if (-not (Test-Path $reportGeneratorPath)) {
    Write-Error "Berichtsgenerator nicht gefunden: $reportGeneratorPath"
    exit 1
}

# Hole die Chargenliste
$chargen = Get-ChargenListe -FilterTyp $FilterTyp.ToLower() -FilterWert $FilterWert

if ($chargen.Count -eq 0) {
    Write-Warning "Keine Chargen gefunden, die dem Filter entsprechen."
    exit 0
}

if (-not $Silent) {
    Write-Info "Gefundene Chargen: $($chargen.Count)"
    
    if ($MaxChargen -gt 0 -and $chargen.Count -gt $MaxChargen) {
        Write-Info "Verarbeitung wird auf $MaxChargen Chargen begrenzt."
    }
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

# Generiere die Berichte
$results = Generate-BatchReports `
    -Chargen $chargen `
    -BerichtTyp $BerichtTyp.ToLower() `
    -ExportFormat $ExportFormat.ToLower() `
    -OutputPath $outputDir `
    -MaxChargen $MaxChargen

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
        -FilterInfo $filterInfo
}

# Abschlussnachricht
if (-not $Silent) {
    Write-Host ""
    Write-Success "Stapelverarbeitung abgeschlossen:"
    Write-Host "  Erfolgreich: $($results.erfolgreich)" -ForegroundColor Green
    Write-Host "  Fehlgeschlagen: $($results.fehlgeschlagen)" -ForegroundColor $(if ($results.fehlgeschlagen -gt 0) { "Red" } else { "Green" })
    Write-Host "  Zusammenfassung: $summaryPath" -ForegroundColor Cyan
    
    # Öffne den Zusammenfassungsbericht
    try {
        Invoke-Item $summaryPath
    }
    catch {
        Write-Warning "Zusammenfassung konnte nicht automatisch geöffnet werden: $($_.Exception.Message)"
    }
}

exit 0 