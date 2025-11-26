***REMOVED*** PowerShell-Skript: Automatisches Hinzufügen von Zurück-Buttons zu Detail-Seiten
***REMOVED*** Findet alle Detail-Seiten ohne Zurück-Button und fügt sie hinzu

$ErrorActionPreference = "Stop"

Write-Host "🔍 Suche nach Detail-Seiten ohne Zurück-Button..." -ForegroundColor Cyan

***REMOVED*** Ziel-Verzeichnisse
$pagesDir = "packages/frontend-web/src/pages"

***REMOVED*** Finde alle TSX-Dateien mit "Detail", "Stamm" oder "Editor" im Namen
$detailPages = Get-ChildItem -Path $pagesDir -Filter "*.tsx" -Recurse | Where-Object {
    $_.Name -match "(detail|stamm|editor)" -and 
    $_.Name -notmatch "(liste|list|overview)"
}

Write-Host "📄 Gefunden: $($detailPages.Count) potenzielle Detail-Seiten" -ForegroundColor Yellow

$processed = 0
$skipped = 0
$added = 0

foreach ($file in $detailPages) {
    $content = Get-Content $file.FullName -Raw
    
    ***REMOVED*** Prüfe ob bereits Zurück-Button vorhanden
    if ($content -match "BackButton|navigate\(-1\)|Zurück zur") {
        Write-Host "✅ Skip: $($file.Name) (hat bereits Zurück-Button)" -ForegroundColor Green
        $skipped++
        continue
    }
    
    ***REMOVED*** Prüfe ob useNavigate importiert ist
    if ($content -notmatch "useNavigate") {
        Write-Host "⚠️  Skip: $($file.Name) (kein useNavigate)" -ForegroundColor Yellow
        $skipped++
        continue
    }
    
    Write-Host "🔧 Verarbeite: $($file.Name)" -ForegroundColor Cyan
    
    ***REMOVED*** 1. Import hinzufügen
    if ($content -match "import.*from '@/components/ui/") {
        $content = $content -replace "(import.*from '@/components/ui/[^']+')(\n)", "`$1`n$2import { BackButton } from '@/components/BackButton'`n"
    }
    
    ***REMOVED*** 2. Zurück-Button zum Header hinzufügen
    ***REMOVED*** Muster: <div><h1>...</h1><p>...</p></div>
    ***REMOVED*** Ersetzen durch: <div class="flex..."><div><h1>...</h1><p>...</p></div><BackButton /></div>
    
    $content = $content -replace `
        '(<div[^>]*>\s*<h1[^>]*>[^<]+</h1>\s*(?:<p[^>]*>[^<]+</p>\s*)?)</div>', `
        '<div className="flex items-center justify-between">$1</div><BackButton /></div>'
    
    ***REMOVED*** Schreibe Datei zurück
    Set-Content -Path $file.FullName -Value $content -NoNewline
    
    $added++
    $processed++
}

Write-Host "`n✅ Fertig!" -ForegroundColor Green
Write-Host "   Verarbeitet: $processed" -ForegroundColor White
Write-Host "   Hinzugefügt: $added" -ForegroundColor Green
Write-Host "   Übersprungen: $skipped" -ForegroundColor Yellow

Write-Host "`n⚠️  ACHTUNG: Bitte prüfe die geänderten Dateien manuell!" -ForegroundColor Red
Write-Host "   - Parent-Routes können falsch sein (standardmäßig navigate(-1))" -ForegroundColor Yellow
Write-Host "   - Layout könnte angepasst werden müssen" -ForegroundColor Yellow
Write-Host "`n💡 Empfehlung: Führe 'pnpm lint:fix' aus" -ForegroundColor Cyan

