#!/bin/bash
# Setup Cursor Browser Permissions
# Automatisch "run this time only" Meldungen umgehen

echo "=== Cursor Browser Permissions Setup ==="
echo ""

# Finde Cursor Settings JSON (Linux/Mac)
if [[ "$OSTYPE" == "darwin"* ]]; then
    SETTINGS_PATH="$HOME/Library/Application Support/Cursor/User/settings.json"
else
    SETTINGS_PATH="$HOME/.config/Cursor/User/settings.json"
fi

if [ ! -f "$SETTINGS_PATH" ]; then
    echo "❌ Cursor Settings nicht gefunden: $SETTINGS_PATH"
    echo "Bitte Cursor einmal öffnen, damit die Settings-Datei erstellt wird."
    exit 1
fi

echo "✅ Settings-Datei gefunden: $SETTINGS_PATH"

# Prüfe ob jq installiert ist
if ! command -v jq &> /dev/null; then
    echo "⚠️ jq ist nicht installiert. Installiere jq..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    else
        sudo apt-get update && sudo apt-get install -y jq
    fi
fi

# Backup erstellen
cp "$SETTINGS_PATH" "${SETTINGS_PATH}.backup"
echo "✅ Backup erstellt: ${SETTINGS_PATH}.backup"

# Setze Browser-Berechtigungen mit jq
jq '. + {
  "cursor.mcp.browser.autoApprove": true,
  "cursor.mcp.browser.trustedDomains": [
    "localhost",
    "127.0.0.1",
    "*.valeo-neuro-erp.local"
  ],
  "cursor.mcp.browser.autoApproveActions": [
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
  ]
}' "$SETTINGS_PATH" > "${SETTINGS_PATH}.tmp" && mv "${SETTINGS_PATH}.tmp" "$SETTINGS_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Settings erfolgreich gespeichert!"
else
    echo "❌ Fehler beim Speichern"
    mv "${SETTINGS_PATH}.backup" "$SETTINGS_PATH"
    exit 1
fi

echo ""
echo "=== Zusammenfassung ==="
echo "✅ autoApprove: true"
echo "✅ trustedDomains: localhost, 127.0.0.1, *.valeo-neuro-erp.local"
echo "✅ autoApproveActions: Alle Browser-Aktionen"
echo ""
echo "⚠️ WICHTIG: Cursor muss neu gestartet werden, damit die Änderungen wirksam werden!"
echo ""
echo "✅ Setup abgeschlossen!"
echo "Bitte starte Cursor neu und teste die Browser-Aktionen."

