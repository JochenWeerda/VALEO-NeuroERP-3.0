#!/bin/bash
# ============================================================================
# VALEO-NeuroERP - MASTER MIGRATION SCRIPT
# Führt alle Alembic-Migrationen für alle CRM-Services aus
# ============================================================================

set -e

echo "🗄️  VALEO-NeuroERP Database Migration Script"
echo "============================================="
echo ""

# Warte auf PostgreSQL
echo "⏳ Warte auf PostgreSQL..."
until pg_isready -h ${POSTGRES_HOST:-postgres} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-valeo_dev} 2>/dev/null; do
  echo "   PostgreSQL ist noch nicht bereit..."
  sleep 2
done
echo "✅ PostgreSQL ist bereit!"
echo ""

# Liste aller Services mit Alembic-Migrationen
SERVICES=(
  "crm-core"
  "crm-sales"
  "crm-service"
  "crm-workflow"
  "crm-analytics"
  "crm-communication"
  "crm-multichannel"
  "crm-marketing"
  "crm-ai"
  "crm-consent"
  "crm-gdpr"
  "inventory"
)

# Zähler für Erfolge/Fehler
SUCCESS_COUNT=0
ERROR_COUNT=0
SKIPPED_COUNT=0

echo "📋 Starte Migrationen für ${#SERVICES[@]} Services..."
echo ""

for SERVICE in "${SERVICES[@]}"; do
  SERVICE_PATH="/app/services/${SERVICE}"
  ALEMBIC_INI="${SERVICE_PATH}/alembic.ini"
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔧 Service: ${SERVICE}"
  
  if [ -f "${ALEMBIC_INI}" ]; then
    echo "   📁 Alembic-Konfiguration gefunden"
    
    cd "${SERVICE_PATH}"
    
    # Prüfe aktuellen Migrations-Status
    CURRENT=$(alembic current 2>/dev/null | grep -oP '\w+' | head -1 || echo "none")
    HEAD=$(alembic heads 2>/dev/null | grep -oP '\w+' | head -1 || echo "unknown")
    
    if [ "$CURRENT" = "$HEAD" ] && [ "$CURRENT" != "none" ]; then
      echo "   ✅ Bereits auf dem neuesten Stand (${CURRENT})"
      ((SKIPPED_COUNT++))
    else
      echo "   ⬆️  Führe Migration aus (${CURRENT} → ${HEAD})..."
      
      if alembic upgrade head 2>&1; then
        echo "   ✅ Migration erfolgreich!"
        ((SUCCESS_COUNT++))
      else
        echo "   ❌ Migration fehlgeschlagen!"
        ((ERROR_COUNT++))
      fi
    fi
  else
    echo "   ⏭️  Keine Alembic-Konfiguration gefunden"
    ((SKIPPED_COUNT++))
  fi
  
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ZUSAMMENFASSUNG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Erfolgreich:  ${SUCCESS_COUNT}"
echo "   ⏭️  Übersprungen: ${SKIPPED_COUNT}"
echo "   ❌ Fehler:       ${ERROR_COUNT}"
echo ""

if [ ${ERROR_COUNT} -gt 0 ]; then
  echo "⚠️  Einige Migrationen sind fehlgeschlagen!"
  exit 1
else
  echo "🎉 Alle Migrationen abgeschlossen!"
  exit 0
fi


