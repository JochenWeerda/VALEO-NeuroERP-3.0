# Setup Cursor Browser Permissions
# Automatisch "run this time only" Meldungen umgehen

Write-Host "=== Cursor Browser Permissions Setup ===" -ForegroundColor Green
Write-Host ""

# Finde Cursor Settings JSON
$settingsPath = "$env:APPDATA\Cursor\User\settings.json"

if (-not (Test-Path $settingsPath)) {
    Write-Host "Cursor Settings nicht gefunden: $settingsPath" -ForegroundColor Red
    Write-Host "Bitte Cursor einmal oeffnen, damit die Settings-Datei erstellt wird." -ForegroundColor Yellow
    exit 1
}

Write-Host "Settings-Datei gefunden: $settingsPath" -ForegroundColor Green

# Lade aktuelle Settings
try {
    $settingsContent = Get-Content $settingsPath -Raw -Encoding UTF8
    $settings = $settingsContent | ConvertFrom-Json
} catch {
    Write-Host "Fehler beim Lesen der Settings. Erstelle neue Settings..." -ForegroundColor Yellow
    $settings = @{} | ConvertTo-Json | ConvertFrom-Json
}

# Setze Browser-Berechtigungen
Write-Host "`nSetze Browser-Berechtigungen..." -ForegroundColor Yellow

# Erstelle Settings-Objekt falls nicht vorhanden
if (-not $settings.PSObject.Properties['cursor']) {
    $settings | Add-Member -MemberType NoteProperty -Name 'cursor' -Value @{} -Force
}

# Setze autoApprove
$settings.cursor | Add-Member -MemberType NoteProperty -Name 'mcp' -Value @{} -Force
$settings.cursor.mcp | Add-Member -MemberType NoteProperty -Name 'browser' -Value @{} -Force
$settings.cursor.mcp.browser | Add-Member -MemberType NoteProperty -Name 'autoApprove' -Value $true -Force

# Setze trustedDomains
$settings.cursor.mcp.browser | Add-Member -MemberType NoteProperty -Name 'trustedDomains' -Value @(
    "localhost",
    "127.0.0.1",
    "*.valeo-neuro-erp.local"
) -Force

# Setze autoApproveActions
$settings.cursor.mcp.browser | Add-Member -MemberType NoteProperty -Name 'autoApproveActions' -Value @(
    "browser_navigate",
    "browser_snapshot",
    "browser_click",
    "browser_type",
    "browser_take_screenshot",
    "browser_console_messages",
    "browser_network_requests",
    "browser_wait_for",
    "browser_hover",
    "browser_select_option",
    "browser_press_key"
) -Force

# Speichere Settings
try {
    $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    Write-Host "Settings erfolgreich gespeichert!" -ForegroundColor Green
} catch {
    Write-Host "Fehler beim Speichern: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Zusammenfassung ===" -ForegroundColor Cyan
Write-Host "autoApprove: true" -ForegroundColor Green
Write-Host "trustedDomains: localhost, 127.0.0.1, *.valeo-neuro-erp.local" -ForegroundColor Green
Write-Host "autoApproveActions: Alle Browser-Aktionen" -ForegroundColor Green

Write-Host "`nWICHTIG: Cursor muss neu gestartet werden, damit die Aenderungen wirksam werden!" -ForegroundColor Yellow
Write-Host "`nDruecke Enter, um Cursor zu schliessen (falls geoeffnet)..." -ForegroundColor White
Read-Host

Write-Host "`nSetup abgeschlossen!" -ForegroundColor Green
Write-Host "Bitte starte Cursor neu und teste die Browser-Aktionen." -ForegroundColor Cyan
