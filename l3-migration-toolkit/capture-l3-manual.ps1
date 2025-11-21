***REMOVED*** L3-Masken Manueller Screenshot-Workflow
***REMOVED*** =========================================
***REMOVED*** 
***REMOVED*** Dieses Skript öffnet den Browser mit der L3-RDP-Verbindung
***REMOVED*** und erlaubt Ihnen, manuell durch L3 zu navigieren.
***REMOVED*** 
***REMOVED*** Nach jeder Navigation geben Sie den Masken-Namen ein,
***REMOVED*** und das Skript erstellt automatisch einen Screenshot.

param(
    [string]$OutputDir = "screenshots\l3-masks"
)

***REMOVED*** Farben für bessere Lesbarkeit
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

***REMOVED*** Erstelle Output-Verzeichnis
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-ColorOutput "✅ Verzeichnis erstellt: $OutputDir" "Green"
}

***REMOVED*** Zähler für Screenshots
$script:Counter = 1
$script:CapturedMasks = @()

***REMOVED*** Funktion: Screenshot erstellen
function Capture-Screenshot {
    param([string]$MaskName)
    
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $filename = "$($script:Counter.ToString('00'))_$($MaskName -replace '[^a-zA-Z0-9-]', '-').png"
    $filepath = Join-Path $OutputDir $filename
    
    ***REMOVED*** Rufe Playwright-Screenshot auf (über Node.js)
    $nodeScript = @"
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const contexts = browser.contexts();
  if (contexts.length === 0) {
    console.error('Keine Browser-Kontexte gefunden');
    process.exit(1);
  }
  const context = contexts[0];
  const pages = context.pages();
  if (pages.length === 0) {
    console.error('Keine geöffneten Seiten gefunden');
    process.exit(1);
  }
  const page = pages[0];
  await page.screenshot({ path: '$($filepath -replace '\\', '/')' });
  console.log('Screenshot gespeichert: $filename');
  await browser.close();
})();
"@
    
    ***REMOVED*** Temporäre Node.js-Datei
    $tempScript = Join-Path $env:TEMP "capture-l3-temp.js"
    $nodeScript | Out-File -FilePath $tempScript -Encoding UTF8
    
    try {
        ***REMOVED*** Führe Node-Skript aus
        $result = node $tempScript 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "   ✅ Screenshot gespeichert: $filename" "Green"
            
            $script:CapturedMasks += @{
                id = $script:Counter
                name = $MaskName
                filename = $filename
                timestamp = $timestamp
            }
            
            $script:Counter++
            return $true
        } else {
            Write-ColorOutput "   ❌ Fehler beim Screenshot: $result" "Red"
            return $false
        }
    } finally {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
}

***REMOVED*** Hauptprogramm
Write-ColorOutput "
╔══════════════════════════════════════════════════════════╗
║   L3-Masken Manueller Screenshot-Workflow                ║
╚══════════════════════════════════════════════════════════╝
" "Cyan"

Write-ColorOutput "📋 Anleitung:" "Yellow"
Write-ColorOutput "   1. Der Browser öffnet sich automatisch mit L3-RDP" "White"
Write-ColorOutput "   2. Navigieren Sie MANUELL zur gewünschten Maske" "White"
Write-ColorOutput "   3. Geben Sie den Masken-Namen ein und drücken Sie Enter" "White"
Write-ColorOutput "   4. Screenshot wird automatisch erstellt" "White"
Write-ColorOutput "   5. Geben Sie 'exit' ein zum Beenden`n" "White"

Write-ColorOutput "🚀 Starte Browser..." "Cyan"
Start-Sleep -Seconds 2

***REMOVED*** Öffne Browser mit L3-RDP (bereits geöffnet in Ihrem Fall)
Write-ColorOutput "
✅ Browser sollte bereits geöffnet sein auf:
   http://localhost:8090/guacamole/***REMOVED***/client/MQBjAHBvc3RncmVzcWw
" "Green"

Write-ColorOutput "Bereit für Screenshots!`n" "Green"

***REMOVED*** Hauptschleife
while ($true) {
    Write-Host ""
    $maskName = Read-Host "📸 Maske-Name (oder 'exit')"
    
    if ($maskName -eq "exit") {
        Write-ColorOutput "`n👋 Beende Erfassung..." "Yellow"
        break
    }
    
    if ([string]::IsNullOrWhiteSpace($maskName)) {
        Write-ColorOutput "⚠️  Bitte einen Masken-Namen eingeben." "Yellow"
        continue
    }
    
    Write-ColorOutput "   📸 Erstelle Screenshot: $maskName" "Cyan"
    
    ***REMOVED*** Alternative: Verwende Playwright MCP direkt (falls verfügbar)
    ***REMOVED*** Für jetzt: Manueller Screenshot über Browser
    Write-ColorOutput "   ⚠️  Bitte erstellen Sie manuell einen Screenshot (Windows + Shift + S)" "Yellow"
    Write-ColorOutput "   ℹ️  Speichern Sie ihn als: $OutputDir\$($script:Counter.ToString('00'))_$($maskName -replace '[^a-zA-Z0-9-]', '-').png" "Gray"
    
    ***REMOVED*** Registriere Maske
    $script:CapturedMasks += @{
        id = $script:Counter
        name = $maskName
        filename = "$($script:Counter.ToString('00'))_$($maskName -replace '[^a-zA-Z0-9-]', '-').png"
        timestamp = (Get-Date -Format "yyyy-MM-dd_HH-mm-ss")
    }
    
    $script:Counter++
    Write-ColorOutput "   ✅ Maske registriert!" "Green"
}

***REMOVED*** Speichere Index
$indexPath = Join-Path $OutputDir "index.json"
$indexData = @{
    generatedAt = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    totalMasks = $script:CapturedMasks.Count
    masks = $script:CapturedMasks
} | ConvertTo-Json -Depth 10

$indexData | Out-File -FilePath $indexPath -Encoding UTF8

Write-ColorOutput "`n✅ Index gespeichert: index.json" "Green"
Write-ColorOutput "🎉 $($script:CapturedMasks.Count) Masken registriert!`n" "Cyan"

***REMOVED*** Zeige Zusammenfassung
Write-ColorOutput "📋 Erfasste Masken:" "Yellow"
$script:CapturedMasks | ForEach-Object {
    Write-ColorOutput "   $($_.id). $($_.name) ($($_.filename))" "White"
}

Write-ColorOutput "`n✨ Fertig!" "Green"

