***REMOVED***!/bin/bash
***REMOVED*** ============================================================================
***REMOVED*** CRM-Core Entrypoint Script
***REMOVED*** Führt Migrationen aus und startet dann den Server
***REMOVED*** ============================================================================

set -e

echo "🚀 CRM-Core Service Starting..."
echo "================================"

***REMOVED*** Warte auf PostgreSQL (einfacher Loop)
echo "⏳ Warte auf PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h postgres -p 5432 -U valeo_dev 2>/dev/null; then
        echo "✅ PostgreSQL ist bereit!"
        break
    fi
    echo "   Versuch $i/30..."
    sleep 2
done

***REMOVED*** Führe Alembic-Migrationen aus
echo ""
echo "📦 Führe Datenbank-Migrationen aus..."
if alembic upgrade head 2>&1; then
    echo "✅ Migrationen erfolgreich!"
else
    echo "⚠️  Migration: Bereits aktuell oder Fehler (ignoriert)"
fi

echo ""
echo "🌐 Starte Uvicorn Server..."
echo "================================"

***REMOVED*** Starte den Server
exec uvicorn main:app --host 0.0.0.0 --port 5600
