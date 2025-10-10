#!/bin/bash
# PostgreSQL Restore Script for VALEO-NeuroERP
# Usage: ./scripts/restore-db.sh <backup_file>

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file.sql.gz>"
  echo "Example: $0 /backups/postgresql/daily/valeo_erp_backup_20251009_120000.sql.gz"
  exit 1
fi

BACKUP_FILE="$1"

# Database connection (from environment)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-valeo_erp}"
DB_USER="${DB_USER:-valeo}"

echo "⚠️  WARNING: This will OVERWRITE the database ${DB_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Restore cancelled"
  exit 0
fi

echo "Starting PostgreSQL restore..."

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
  echo "Error: Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

# Create a safety backup before restore
SAFETY_BACKUP="/tmp/valeo_erp_pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
echo "Creating safety backup: ${SAFETY_BACKUP}"
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
  --format=plain --no-owner --no-acl \
  | gzip > "${SAFETY_BACKUP}"

echo "Safety backup created: ${SAFETY_BACKUP}"

# Drop and recreate database
echo "Dropping database ${DB_NAME}..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres \
  -c "DROP DATABASE IF EXISTS ${DB_NAME};"

echo "Creating database ${DB_NAME}..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres \
  -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

# Restore from backup
echo "Restoring from backup..."
gunzip -c "${BACKUP_FILE}" | psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}"

echo "Restore completed successfully"

# Verify restore
echo "Verifying restore..."
TABLE_COUNT=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
  -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")

echo "Tables restored: ${TABLE_COUNT}"

if [ "${TABLE_COUNT}" -eq 0 ]; then
  echo "⚠️  WARNING: No tables found after restore. Restore may have failed."
  echo "Safety backup available at: ${SAFETY_BACKUP}"
  exit 1
fi

echo "✅ Restore verification successful"
echo "Safety backup kept at: ${SAFETY_BACKUP}"
echo ""
echo "Next steps:"
echo "1. Test the application"
echo "2. If successful, delete safety backup: rm ${SAFETY_BACKUP}"
echo "3. If failed, restore from safety backup"

