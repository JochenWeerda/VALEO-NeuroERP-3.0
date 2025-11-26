***REMOVED***!/bin/bash
***REMOVED*** Bash Script: CRM Migration 003 - Sales Fields
***REMOVED*** Führt die Migration für SALES-CRM-02 aus

set -e

***REMOVED*** Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' ***REMOVED*** No Color

echo -e "${CYAN}🚀 CRM Migration 003: Sales Fields (SALES-CRM-02)${NC}"
echo -e "${CYAN}============================================================${NC}"

***REMOVED*** Migration-Script-Pfad
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="$SCRIPT_DIR/../migrations/sql/crm/003_add_sales_fields_to_customers.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}❌ Migration-Script nicht gefunden: $MIGRATION_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}📄 Migration-Script: $MIGRATION_FILE${NC}"

***REMOVED*** Datenbankverbindung
if [ -n "$DATABASE_URL" ]; then
    echo -e "${YELLOW}🔌 Verwende DATABASE_URL${NC}"
    psql "$DATABASE_URL" -f "$MIGRATION_FILE"
elif [ -n "$PGHOST" ] && [ -n "$PGDATABASE" ] && [ -n "$PGUSER" ]; then
    echo -e "${YELLOW}🔌 Verbinde zur Datenbank...${NC}"
    echo -e "   Host: ${PGHOST:-localhost}${NC}"
    echo -e "   Database: ${PGDATABASE}${NC}"
    psql -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "$PGUSER" -d "$PGDATABASE" -f "$MIGRATION_FILE"
else
    echo -e "${RED}❌ Keine Datenbankverbindung konfiguriert${NC}"
    echo -e "${YELLOW}💡 Setze DATABASE_URL oder PGHOST/PGDATABASE/PGUSER${NC}"
    echo -e "${YELLOW}   Beispiel: export DATABASE_URL='postgresql://user:pass@host:port/dbname'${NC}"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Migration erfolgreich abgeschlossen!${NC}"
    echo ""
    echo -e "${CYAN}Hinzugefügte Felder:${NC}"
    echo -e "  - price_group (VARCHAR(50))"
    echo -e "  - tax_category (VARCHAR(50))"
    echo ""
    echo -e "${CYAN}Indizes erstellt:${NC}"
    echo -e "  - idx_crm_customers_price_group"
    echo -e "  - idx_crm_customers_tax_category"
else
    echo ""
    echo -e "${RED}❌ Migration fehlgeschlagen${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Migration 003 abgeschlossen!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

