# MCP Browser Berechtigungen - "Run this time only" umgehen

## Problem

Bei der Verwendung des MCP Browser-Tools in Cursor erscheinen "run this time only" Meldungen, die bei jeder Ausführung bestätigt werden müssen.

## Lösungen

### Lösung 1: Cursor-Einstellungen (Empfohlen)

1. **Cursor-Einstellungen öffnen:**
   - `File > Preferences > Settings` (oder `Ctrl+,`)
   - Oder: `Cmd+,` auf Mac

2. **Suche nach Browser-Berechtigungen:**
   - Suche nach: `browser` oder `permissions` oder `mcp`
   - Oder direkt: `cursor.mcp.browser.autoApprove`

3. **Berechtigungen aktivieren:**
   - Setze `cursor.mcp.browser.autoApprove` auf `true`
   - Oder: `mcp.browser.autoApproveActions` auf `true`

### Lösung 2: Cursor Settings JSON

1. **Settings JSON öffnen:**
   - `Ctrl+Shift+P` (oder `Cmd+Shift+P` auf Mac)
   - Tippe: `Preferences: Open User Settings (JSON)`

2. **Folgende Einstellungen hinzufügen:**

```json
{
  "cursor.mcp.browser.autoApprove": true,
  "cursor.mcp.browser.autoApproveActions": [
    "browser_navigate",
    "browser_snapshot",
    "browser_click",
    "browser_type",
    "browser_take_screenshot",
    "browser_console_messages",
    "browser_network_requests"
  ],
  "cursor.mcp.browser.trustedDomains": [
    "localhost",
    "127.0.0.1",
    "*.valeo-neuro-erp.local"
  ]
}
```

### Lösung 3: Workspace-spezifische Einstellungen

Erstelle eine `.vscode/settings.json` im Projekt-Root:

```json
{
  "cursor.mcp.browser.autoApprove": true,
  "cursor.mcp.browser.autoApproveActions": "*",
  "cursor.mcp.browser.trustedDomains": [
    "localhost",
    "127.0.0.1"
  ]
}
```

### Lösung 4: MCP-Server-Konfiguration

Falls der MCP-Server eine Konfigurationsdatei hat, füge dort hinzu:

```json
{
  "browser": {
    "autoApprove": true,
    "trustedDomains": ["localhost", "127.0.0.1"],
    "autoApproveActions": [
      "navigate",
      "snapshot",
      "click",
      "type",
      "screenshot"
    ]
  }
}
```

## Verifikation

Nach dem Setzen der Einstellungen:

1. **Cursor neu starten** (wichtig!)
2. **MCP Browser-Tool testen:**
   ```typescript
   // Sollte ohne Bestätigung funktionieren
   mcp_cursor-ide-browser_browser_navigate({ url: "http://localhost:3000" })
   ```

3. **Prüfe, ob keine Dialoge mehr erscheinen**

## Troubleshooting

### Problem: Einstellungen werden nicht übernommen

**Lösung:**
- Cursor komplett neu starten
- Prüfe, ob die Einstellungen in der JSON-Datei korrekt sind
- Prüfe, ob es Konflikte mit anderen Einstellungen gibt

### Problem: Nur bestimmte Aktionen werden automatisch genehmigt

**Lösung:**
- Erweitere die `autoApproveActions` Liste
- Oder setze `autoApproveActions: "*"` für alle Aktionen

### Problem: Sicherheitswarnungen erscheinen weiterhin

**Lösung:**
- Füge die Domains zu `trustedDomains` hinzu
- Prüfe, ob die Domain-Formatierung korrekt ist (mit/ohne Protokoll)

## Best Practices

1. **Nur vertrauenswürdige Domains hinzufügen:**
   - Nicht für öffentliche/unsichere Domains verwenden
   - Nur für lokale Entwicklung (`localhost`, `127.0.0.1`)

2. **Granulare Berechtigungen:**
   - Statt `*` für alle Aktionen, spezifische Aktionen auflisten
   - Erhöht die Sicherheit

3. **Workspace-spezifisch:**
   - Verwende `.vscode/settings.json` für projektspezifische Einstellungen
   - Nicht global für alle Projekte

## Alternative: Script-basierte Lösung

Falls die Einstellungen nicht funktionieren, kann ein Script die Berechtigungen setzen:

```powershell
# Windows PowerShell
$settingsPath = "$env:APPDATA\Cursor\User\settings.json"
$settings = Get-Content $settingsPath | ConvertFrom-Json
$settings.'cursor.mcp.browser.autoApprove' = $true
$settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
```

```bash
# Linux/Mac
# Cursor Settings JSON bearbeiten
jq '. + {"cursor.mcp.browser.autoApprove": true}' ~/.config/Cursor/User/settings.json > /tmp/settings.json
mv /tmp/settings.json ~/.config/Cursor/User/settings.json
```

## Weitere Informationen

- [Cursor MCP Documentation](https://docs.cursor.com/mcp)
- [MCP Browser Tool Reference](https://modelcontextprotocol.io/tools/browser)

