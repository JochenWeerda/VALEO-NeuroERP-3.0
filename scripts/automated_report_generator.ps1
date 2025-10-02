***REMOVED*** ===================================================
***REMOVED*** Automatisierter Chargenbericht-Generator
***REMOVED*** ===================================================
***REMOVED*** Erstellt automatisierte Berichte für Chargen
***REMOVED*** basierend auf verschiedenen Berichtstypen
***REMOVED*** ===================================================

***REMOVED*** Lade Hilfsfunktionen
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptPath\powershell_compatibility.ps1"

***REMOVED*** Banner anzeigen
Write-Host ""
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host "  Automatisierter Chargenbericht-Generator" -ForegroundColor Cyan
Write-Host " =====================================================" -ForegroundColor Cyan
Write-Host ""

***REMOVED*** Parameter definieren
param (
    [string]$ChargeId = "",
    [string]$BerichtTyp = "zusammenfassung",
    [string]$ExportFormat = "pdf",
    [string]$OutputPath = "",
    [switch]$Silent = $false,
    [switch]$Scheduled = $false
)

***REMOVED*** Pfade definieren
$rootDir = Split-Path -Parent $scriptPath
$frontendDir = Join-Path $rootDir "frontend"
$apiEndpoint = "http://localhost:8003/api/v1/chargen"
$outputDir = if ($OutputPath) { $OutputPath } else { Join-Path $rootDir "reports" }

***REMOVED*** Überprüfe, ob der Ausgabepfad existiert
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Success "Berichtsverzeichnis erstellt: $outputDir"
}

***REMOVED*** Verfügbare Berichtstypen
$verfuegbareBerichtstypen = @(
    "zusammenfassung", 
    "qualitaet", 
    "rueckverfolgung", 
    "lager", 
    "produktion"
)

***REMOVED*** Funktionen
function Get-Charge {
    param (
        [string]$ChargeId
    )
    
    try {
        $endpoint = "$apiEndpoint/$ChargeId"
        $response = Invoke-RestMethod -Uri $endpoint -Method Get -ContentType "application/json"
        return $response
    }
    catch {
        Write-Error "Fehler beim Abrufen der Charge: $($_.Exception.Message)"
        return $null
    }
}

function Get-ChargenListe {
    try {
        $response = Invoke-RestMethod -Uri $apiEndpoint -Method Get -ContentType "application/json"
        return $response
    }
    catch {
        Write-Error "Fehler beim Abrufen der Chargenliste: $($_.Exception.Message)"
        return @()
    }
}

function Generate-Bericht {
    param (
        [PSObject]$Charge,
        [string]$BerichtTyp,
        [string]$ExportFormat
    )
    
    $fileName = "Charge_$(if ($Charge.chargenNummer) {$Charge.chargenNummer} else {$Charge.id})_$BerichtTyp"
    $outputFile = Join-Path $outputDir "$fileName.$ExportFormat"
    
    Write-Info "Generiere $BerichtTyp-Bericht für Charge $($Charge.id)..."
    
    switch ($BerichtTyp) {
        "zusammenfassung" { Generate-ZusammenfassungsBericht $Charge $outputFile $ExportFormat }
        "qualitaet" { Generate-QualitaetsBericht $Charge $outputFile $ExportFormat }
        "rueckverfolgung" { Generate-RueckverfolgungsBericht $Charge $outputFile $ExportFormat }
        "lager" { Generate-LagerBericht $Charge $outputFile $ExportFormat }
        "produktion" { Generate-ProduktionsBericht $Charge $outputFile $ExportFormat }
        default { Write-Error "Unbekannter Berichtstyp: $BerichtTyp"; return $null }
    }
    
    if (Test-Path $outputFile) {
        Write-Success "Bericht erfolgreich erstellt: $outputFile"
        return $outputFile
    }
    else {
        Write-Error "Fehler beim Erstellen des Berichts"
        return $null
    }
}

function Generate-ZusammenfassungsBericht {
    param (
        [PSObject]$Charge,
        [string]$OutputFile,
        [string]$Format
    )
    
    ***REMOVED*** Berichtsinhalt erstellen
    $reportContent = @"
***REMOVED*** Zusammenfassender Chargenbericht

***REMOVED******REMOVED*** Chargeninformationen
- **Chargen-ID:** $($Charge.id)
- **Chargennummer:** $($Charge.chargenNummer)
- **Artikel:** $($Charge.artikelBezeichnung)
- **Menge:** $($Charge.menge) $($Charge.einheit)
- **Erstellungsdatum:** $($Charge.erstellungsDatum)
- **Status:** $($Charge.status)

***REMOVED******REMOVED*** Qualität
- **Qualitätsstatus:** $($Charge.qualitaetsStatus)
- **Prüfdatum:** $($Charge.pruefDatum)

***REMOVED******REMOVED*** Lagerstatus
- **Aktueller Lagerort:** $($Charge.lagerort)
- **Verfügbare Menge:** $($Charge.verfuegbareMenge) $($Charge.einheit)

***REMOVED******REMOVED*** Rückverfolgbarkeit
- **Herkunft:** $($Charge.herkunft)
- **Verknüpfte Chargen:** $($Charge.verknuepfteChargen.Count)
"@

    ***REMOVED*** Bericht speichern
    switch ($Format) {
        "pdf" { Export-ToPDF $reportContent $OutputFile }
        "csv" { Export-ToCSV $Charge $OutputFile }
        "json" { Export-ToJSON $Charge $OutputFile }
        "html" { Export-ToHTML $reportContent $OutputFile }
        "txt" { Set-Content -Path $OutputFile -Value $reportContent }
        default { Set-Content -Path $OutputFile -Value $reportContent }
    }
}

function Generate-QualitaetsBericht {
    param (
        [PSObject]$Charge,
        [string]$OutputFile,
        [string]$Format
    )
    
    ***REMOVED*** Berichtsinhalt erstellen
    $reportContent = @"
***REMOVED*** Qualitätsbericht für Charge $($Charge.chargenNummer)

***REMOVED******REMOVED*** Chargeninformationen
- **Chargen-ID:** $($Charge.id)
- **Chargennummer:** $($Charge.chargenNummer)
- **Artikel:** $($Charge.artikelBezeichnung)

***REMOVED******REMOVED*** Qualitätsparameter
- **Qualitätsstatus:** $($Charge.qualitaetsStatus)
- **Prüfdatum:** $($Charge.pruefDatum)
- **Prüfer:** $($Charge.pruefer)

***REMOVED******REMOVED*** Messwerte
$(if ($Charge.qualitaetsparameter) {
    foreach ($param in $Charge.qualitaetsparameter) {
        "- **$($param.name):** $($param.wert) $($param.einheit) (Soll: $($param.sollWert) $($param.einheit))`n"
    }
})

***REMOVED******REMOVED*** Bemerkungen
$($Charge.qualitaetsBemerkungen)
"@

    ***REMOVED*** Bericht speichern
    switch ($Format) {
        "pdf" { Export-ToPDF $reportContent $OutputFile }
        "csv" { Export-ToCSV $Charge.qualitaetsparameter $OutputFile }
        "json" { Export-ToJSON $Charge.qualitaetsparameter $OutputFile }
        "html" { Export-ToHTML $reportContent $OutputFile }
        "txt" { Set-Content -Path $OutputFile -Value $reportContent }
        default { Set-Content -Path $OutputFile -Value $reportContent }
    }
}

function Generate-RueckverfolgungsBericht {
    param (
        [PSObject]$Charge,
        [string]$OutputFile,
        [string]$Format
    )
    
    ***REMOVED*** Berichtsinhalt erstellen
    $reportContent = @"
***REMOVED*** Rückverfolgungsbericht für Charge $($Charge.chargenNummer)

***REMOVED******REMOVED*** Chargeninformationen
- **Chargen-ID:** $($Charge.id)
- **Chargennummer:** $($Charge.chargenNummer)
- **Artikel:** $($Charge.artikelBezeichnung)
- **Erstellungsdatum:** $($Charge.erstellungsDatum)

***REMOVED******REMOVED*** Herkunft
- **Lieferant:** $($Charge.lieferant)
- **Herkunftsdatum:** $($Charge.herkunftsDatum)
- **Herkunfts-ID:** $($Charge.herkunftsID)

***REMOVED******REMOVED*** Vorwärts-Verfolgung
$(if ($Charge.vorwaertsVerfolgung) {
    foreach ($item in $Charge.vorwaertsVerfolgung) {
        "- **$($item.typ):** $($item.chargenNummer) ($($item.datum))`n"
    }
})

***REMOVED******REMOVED*** Rückwärts-Verfolgung
$(if ($Charge.rueckwaertsVerfolgung) {
    foreach ($item in $Charge.rueckwaertsVerfolgung) {
        "- **$($item.typ):** $($item.chargenNummer) ($($item.datum))`n"
    }
})

***REMOVED******REMOVED*** Prozessschritte
$(if ($Charge.prozessSchritte) {
    foreach ($step in $Charge.prozessSchritte) {
        "- **$($step.name):** $($step.datum) ($($step.status))`n"
    }
})
"@

    ***REMOVED*** Bericht speichern
    switch ($Format) {
        "pdf" { Export-ToPDF $reportContent $OutputFile }
        "csv" { 
            $data = @()
            if ($Charge.vorwaertsVerfolgung) { $data += $Charge.vorwaertsVerfolgung }
            if ($Charge.rueckwaertsVerfolgung) { $data += $Charge.rueckwaertsVerfolgung }
            Export-ToCSV $data $OutputFile 
        }
        "json" { 
            $data = @{
                vorwaertsVerfolgung = $Charge.vorwaertsVerfolgung
                rueckwaertsVerfolgung = $Charge.rueckwaertsVerfolgung
            }
            Export-ToJSON $data $OutputFile 
        }
        "html" { Export-ToHTML $reportContent $OutputFile }
        "txt" { Set-Content -Path $OutputFile -Value $reportContent }
        default { Set-Content -Path $OutputFile -Value $reportContent }
    }
}

function Generate-LagerBericht {
    param (
        [PSObject]$Charge,
        [string]$OutputFile,
        [string]$Format
    )
    
    ***REMOVED*** Berichtsinhalt erstellen
    $reportContent = @"
***REMOVED*** Lagerbericht für Charge $($Charge.chargenNummer)

***REMOVED******REMOVED*** Chargeninformationen
- **Chargen-ID:** $($Charge.id)
- **Chargennummer:** $($Charge.chargenNummer)
- **Artikel:** $($Charge.artikelBezeichnung)
- **Menge:** $($Charge.menge) $($Charge.einheit)

***REMOVED******REMOVED*** Aktueller Lagerstatus
- **Lagerort:** $($Charge.lagerort)
- **Verfügbare Menge:** $($Charge.verfuegbareMenge) $($Charge.einheit)
- **Reservierte Menge:** $($Charge.reservierteMenge) $($Charge.einheit)

***REMOVED******REMOVED*** Lagerbewegungen
$(if ($Charge.lagerBewegungen) {
    foreach ($bewegung in $Charge.lagerBewegungen) {
        "- **$($bewegung.typ):** $($bewegung.menge) $($bewegung.einheit) am $($bewegung.datum) - $($bewegung.lagerort)`n"
    }
})

***REMOVED******REMOVED*** Reservierungen
$(if ($Charge.reservierungen) {
    foreach ($res in $Charge.reservierungen) {
        "- **$($res.typ):** $($res.menge) $($res.einheit) für $($res.ziel) bis $($res.bisDate)`n"
    }
})
"@

    ***REMOVED*** Bericht speichern
    switch ($Format) {
        "pdf" { Export-ToPDF $reportContent $OutputFile }
        "csv" { Export-ToCSV $Charge.lagerBewegungen $OutputFile }
        "json" { 
            $data = @{
                lagerBewegungen = $Charge.lagerBewegungen
                reservierungen = $Charge.reservierungen
            }
            Export-ToJSON $data $OutputFile 
        }
        "html" { Export-ToHTML $reportContent $OutputFile }
        "txt" { Set-Content -Path $OutputFile -Value $reportContent }
        default { Set-Content -Path $OutputFile -Value $reportContent }
    }
}

function Generate-ProduktionsBericht {
    param (
        [PSObject]$Charge,
        [string]$OutputFile,
        [string]$Format
    )
    
    ***REMOVED*** Berichtsinhalt erstellen
    $reportContent = @"
***REMOVED*** Produktionsbericht für Charge $($Charge.chargenNummer)

***REMOVED******REMOVED*** Chargeninformationen
- **Chargen-ID:** $($Charge.id)
- **Chargennummer:** $($Charge.chargenNummer)
- **Artikel:** $($Charge.artikelBezeichnung)
- **Menge:** $($Charge.menge) $($Charge.einheit)

***REMOVED******REMOVED*** Produktionsdaten
- **Produktionsauftrag:** $($Charge.produktionsAuftrag)
- **Produktionsdatum:** $($Charge.produktionsDatum)
- **Produktionslinie:** $($Charge.produktionsLinie)
- **Verantwortlicher:** $($Charge.produktionsVerantwortlicher)

***REMOVED******REMOVED*** Verwendete Materialien
$(if ($Charge.materialien) {
    foreach ($material in $Charge.materialien) {
        "- **$($material.artikelBezeichnung):** $($material.menge) $($material.einheit) (Charge: $($material.chargenNummer))`n"
    }
})

***REMOVED******REMOVED*** Prozessparameter
$(if ($Charge.prozessParameter) {
    foreach ($param in $Charge.prozessParameter) {
        "- **$($param.name):** $($param.wert) $($param.einheit)`n"
    }
})

***REMOVED******REMOVED*** Protokoll
$($Charge.produktionsProtokoll)
"@

    ***REMOVED*** Bericht speichern
    switch ($Format) {
        "pdf" { Export-ToPDF $reportContent $OutputFile }
        "csv" { Export-ToCSV $Charge.materialien $OutputFile }
        "json" { 
            $data = @{
                materialien = $Charge.materialien
                prozessParameter = $Charge.prozessParameter
                protokoll = $Charge.produktionsProtokoll
            }
            Export-ToJSON $data $OutputFile 
        }
        "html" { Export-ToHTML $reportContent $OutputFile }
        "txt" { Set-Content -Path $OutputFile -Value $reportContent }
        default { Set-Content -Path $OutputFile -Value $reportContent }
    }
}

function Export-ToPDF {
    param (
        [string]$Content,
        [string]$OutputFile
    )
    
    ***REMOVED*** Hier würde die eigentliche PDF-Generierung stattfinden
    ***REMOVED*** Da das in PowerShell etwas komplexer ist, hier nur eine Simulation
    $htmlFile = $OutputFile -replace '\.pdf$', '.html'
    Export-ToHTML $Content $htmlFile
    
    ***REMOVED*** Conversion to PDF (in real-world scenario would use a library like PuppeteerSharp, etc.)
    ***REMOVED*** Here we just use HTML as a placeholder
    Write-Info "PDF-Generierung simuliert mit HTML als Ersatz: $htmlFile"
    Copy-Item $htmlFile $OutputFile
    Remove-Item $htmlFile
}

function Export-ToCSV {
    param (
        [PSObject]$Data,
        [string]$OutputFile
    )
    
    if ($Data -is [array] -and $Data.Count -gt 0) {
        $Data | Export-Csv -Path $OutputFile -NoTypeInformation
    }
    else {
        ***REMOVED*** Fallback wenn keine Array-Daten vorhanden sind
        $Data | ConvertTo-Json | Set-Content -Path $OutputFile
    }
}

function Export-ToJSON {
    param (
        [PSObject]$Data,
        [string]$OutputFile
    )
    
    $Data | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputFile
}

function Export-ToHTML {
    param (
        [string]$Content,
        [string]$OutputFile
    )
    
    ***REMOVED*** Einfache Konvertierung von Markdown-ähnlichem Format zu HTML
    $htmlContent = $Content -replace '***REMOVED*** (.*)', '<h1>$1</h1>'
    $htmlContent = $htmlContent -replace '***REMOVED******REMOVED*** (.*)', '<h2>$1</h2>'
    $htmlContent = $htmlContent -replace '- \*\*(.*?):\*\* (.*)', '<p><strong>$1:</strong> $2</p>'
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chargenbericht</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: ***REMOVED***2c3e50; border-bottom: 1px solid ***REMOVED***eee; padding-bottom: 10px; }
        h2 { color: ***REMOVED***3498db; margin-top: 30px; }
        p { margin: 5px 0; }
        strong { color: ***REMOVED***444; }
    </style>
</head>
<body>
    $htmlContent
</body>
</html>
"@
    
    Set-Content -Path $OutputFile -Value $html
}

***REMOVED*** Hauptlogik
if (-not $Silent) {
    Write-Info "Automatisierter Chargenbericht-Generator gestartet"
}

***REMOVED*** Wenn keine Charge-ID angegeben wurde, alle Chargen anzeigen
if (-not $ChargeId) {
    $chargen = Get-ChargenListe
    
    if ($chargen.Count -eq 0) {
        Write-Warning "Keine Chargen gefunden."
        exit 0
    }
    
    if (-not $Silent) {
        Write-Info "Verfügbare Chargen:"
        foreach ($charge in $chargen) {
            Write-Host "  - $($charge.id): $($charge.chargenNummer) - $($charge.artikelBezeichnung)" -ForegroundColor White
        }
        
        Write-Info "Verfügbare Berichtstypen:"
        foreach ($typ in $verfuegbareBerichtstypen) {
            Write-Host "  - $typ" -ForegroundColor White
        }
        
        Write-Info "Beispielaufruf:"
        Write-Host "  ./automated_report_generator.ps1 -ChargeId CHG-12345 -BerichtTyp qualitaet -ExportFormat pdf" -ForegroundColor White
    }
    
    exit 0
}

***REMOVED*** Verarbeite die angegebene Charge
$charge = Get-Charge -ChargeId $ChargeId

if (-not $charge) {
    Write-Error "Charge mit ID $ChargeId nicht gefunden."
    exit 1
}

***REMOVED*** Überprüfe, ob der Berichtstyp gültig ist
if (-not $verfuegbareBerichtstypen.Contains($BerichtTyp.ToLower())) {
    Write-Error "Ungültiger Berichtstyp: $BerichtTyp. Verfügbar sind: $($verfuegbareBerichtstypen -join ', ')"
    exit 1
}

***REMOVED*** Generiere den Bericht
$outputFile = Generate-Bericht -Charge $charge -BerichtTyp $BerichtTyp.ToLower() -ExportFormat $ExportFormat.ToLower()

if ($outputFile -and -not $Silent) {
    Write-Success "Bericht wurde erfolgreich erstellt: $outputFile"
    
    ***REMOVED*** Öffne den Bericht, wenn er erfolgreich erstellt wurde
    if (-not $Scheduled) {
        try {
            Invoke-Item $outputFile
        }
        catch {
            Write-Warning "Datei konnte nicht automatisch geöffnet werden: $($_.Exception.Message)"
        }
    }
}

exit 0 