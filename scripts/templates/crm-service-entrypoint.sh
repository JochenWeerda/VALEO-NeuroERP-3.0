***REMOVED***!/bin/bash
***REMOVED*** ============================================================================
***REMOVED*** CRM Service Entrypoint Script (Template)
***REMOVED*** Führt Migrationen aus und startet dann den Server
***REMOVED*** 
***REMOVED*** Umgebungsvariablen:
***REMOVED***   DATABASE_URL - PostgreSQL Connection String
***REMOVED***   SERVICE_PORT - Port für den Service (default: 5600)
***REMOVED***   SERVICE_NAME - Name des Services für Logging
***REMOVED*** ============================================================================

set -e

SERVICE_NAME="${SERVICE_NAME:-crm-service}"
SERVICE_PORT="${SERVICE_PORT:-5600}"

echo "🚀 ${SERVICE_NAME} Starting..."
echo "================================"

***REMOVED*** Extrahiere DB-Host aus verschiedenen möglichen Umgebungsvariablen
if [ -n "$CRM_CORE_DATABASE_URL" ]; then
    DB_URL="$CRM_CORE_DATABASE_URL"
elif [ -n "$DATABASE_URL" ]; then
    DB_URL="$DATABASE_URL"
else
    echo "❌ Keine DATABASE_URL gefunden!"
    exit 1
fi

DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

echo "⏳ Warte auf PostgreSQL (${DB_HOST}:${DB_PORT})..."

***REMOVED*** Warte auf PostgreSQL mit Python
python -c "
import socket
import time
import sys

host = '${DB_HOST:-postgres}'
port = int('${DB_PORT:-5432}')
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f'✅ PostgreSQL ist bereit!')
            sys.exit(0)
    except:
        pass
    retry_count += 1
    print(f'   Versuch {retry_count}/{max_retries}...')
    time.sleep(2)

print('❌ PostgreSQL nicht erreichbar nach {max_retries} Versuchen!')
sys.exit(1)
"

***REMOVED*** Führe Alembic-Migrationen aus (falls vorhanden)
if [ -f "alembic.ini" ]; then
    echo ""
    echo "📦 Führe Datenbank-Migrationen aus..."
    if alembic upgrade head 2>&1; then
        echo "✅ Migrationen erfolgreich!"
    else
        echo "⚠️  Migration fehlgeschlagen oder bereits aktuell"
    fi
else
    echo "ℹ️  Keine Alembic-Konfiguration gefunden, überspringe Migrationen"
fi

echo ""
echo "🌐 Starte Uvicorn Server auf Port ${SERVICE_PORT}..."
echo "================================"

***REMOVED*** Starte den Server
exec uvicorn main:app --host 0.0.0.0 --port ${SERVICE_PORT}

