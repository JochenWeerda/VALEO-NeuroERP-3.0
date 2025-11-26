#!/bin/sh
# Temporäres Script zur Fehlereingrenzung - Pipeline im Container testen
set -e

echo "🚀 Starte GAP-Import im Container..."
echo "📊 Datenbank: $DATABASE_URL"

# Prüfe ob CSV vorhanden
if [ ! -f "/tmp/impdata2024.csv" ]; then
  echo "❌ CSV-Datei nicht gefunden: /tmp/impdata2024.csv"
  exit 1
fi

echo "✅ CSV-Datei gefunden"
echo "📝 Starte Import..."

# Einfacher Test: Prüfe ob Verbindung funktioniert
psql "$DATABASE_URL" -c "SELECT 1 as test;" || {
  echo "❌ Datenbankverbindung fehlgeschlagen"
  exit 1
}

echo "✅ Datenbankverbindung erfolgreich"
echo "💡 Für vollständigen Import: Node.js-Script im Container ausführen"
echo "   oder Pipeline über Backend-API aufrufen"

