#!/bin/bash
# CRM-GDPR Entrypoint - Führt Migrationen aus und startet den Server
set -e

echo "🚀 CRM-GDPR Service Starting..."

# Warte auf PostgreSQL
echo "⏳ Warte auf PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h postgres -p 5432 -U valeo_dev 2>/dev/null; then
        echo "✅ PostgreSQL ist bereit!"
        break
    fi
    echo "   Versuch $i/30..."
    sleep 2
done

# Führe Alembic-Migrationen aus
echo "📦 Führe Datenbank-Migrationen aus..."
if alembic upgrade head 2>&1; then
    echo "✅ Migrationen erfolgreich!"
else
    echo "⚠️  Migration: Bereits aktuell oder Fehler"
fi

echo "🌐 Starte Server..."
exec python main.py


