#!/usr/bin/env sh
set -e

echo "🚀 Inventory Service Starting..."

# Warte auf PostgreSQL
if [ -n "${INVENTORY_DATABASE_URL}" ]; then
  echo "⏳ Warte auf PostgreSQL..."
  for i in $(seq 1 30); do
    if pg_isready -h postgres -p 5432 -U valeo_dev 2>/dev/null; then
      echo "✅ PostgreSQL ist bereit!"
      break
    fi
    echo "   Versuch $i/30..."
    sleep 2
  done
  
  # Run Alembic migrations
  echo "📦 Führe Datenbank-Migrationen aus..."
  if alembic -c /app/alembic.ini upgrade head 2>&1; then
    echo "✅ Migrationen erfolgreich!"
  else
    echo "⚠️  Migration: Bereits aktuell oder Fehler"
  fi
else
  echo "ℹ️  INVENTORY_DATABASE_URL nicht gesetzt, überspringe Migrationen."
fi

echo "🌐 Starte Server..."
exec "$@"


