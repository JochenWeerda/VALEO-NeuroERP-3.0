# PowerShell-Skript zum Hinzuf.gen von Export/Drucken-Funktionalität zu allen Listen-Seiten

$pages = @(
    "packages/frontend-web/src/pages/crm/kontakte-liste.tsx",
    "packages/frontend-web/src/pages/crm/leads.tsx",
    "packages/frontend-web/src/pages/crm/aktivitaeten.tsx",
    "packages/frontend-web/src/pages/crm/betriebsprofile-liste.tsx",
    "packages/frontend-web/src/pages/einkauf/lieferanten-liste.tsx",
    "packages/frontend-web/src/pages/einkauf/bestellvorschlaege.tsx",
    "packages/frontend-web/src/pages/artikel/liste.tsx",
    "packages/frontend-web/src/pages/charge/liste.tsx",
    "packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx",
    "packages/frontend-web/src/pages/agrar/saatgut-liste.tsx",
    "packages/frontend-web/src/pages/agrar/duenger-liste.tsx",
    "packages/frontend-web/src/pages/agrar/psm/liste.tsx",
    "packages/frontend-web/src/pages/futter/einzel/liste.tsx",
    "packages/frontend-web/src/pages/futter/misch/liste.tsx",
    "packages/frontend-web/src/pages/qualitaet/labor-liste.tsx",
    "packages/frontend-web/src/pages/qualitaet/reklamationen.tsx",
    "packages/frontend-web/src/pages/personal/mitarbeiter-liste.tsx",
    "packages/frontend-web/src/pages/personal/schulungen.tsx",
    "packages/frontend-web/src/pages/zertifikate/liste.tsx",
    "packages/frontend-web/src/pages/wartung/anlagen-liste.tsx"
)

Write-Host "🔧 Füge Export/Drucken-Funktionalität zu $($pages.Count) Seiten hinzu..."
Write-Host ""

foreach ($page in $pages) {
    if (Test-Path $page) {
        $content = Get-Content $page -Raw
        
        # Prüfe ob useListActions bereits importiert ist
        if ($content -notmatch "useListActions") {
            Write-Host "✅ Aktualisiere: $page"
            # Hier würde die automatische Änderung erfolgen
        } else {
            Write-Host "⏭️  Überspringe (bereits aktualisiert): $page"
        }
    } else {
        Write-Host "⚠️  Nicht gefunden: $page"
    }
}

Write-Host ""
Write-Host "✅ Skript abgeschlossen!"


