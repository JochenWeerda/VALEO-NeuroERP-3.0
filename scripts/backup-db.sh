#!/bin/bash
# PostgreSQL Backup Script for VALEO-NeuroERP
# Usage: ./scripts/backup-db.sh

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups/postgresql}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
RETENTION_MONTHS="${RETENTION_MONTHS:-12}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="valeo_erp_backup_${TIMESTAMP}.sql.gz"

# Database connection (from environment)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-valeo_erp}"
DB_USER="${DB_USER:-valeo}"

echo "Starting PostgreSQL backup..."
echo "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "Backup file: ${BACKUP_FILE}"

# Create backup directory
mkdir -p "${BACKUP_DIR}/daily"
mkdir -p "${BACKUP_DIR}/monthly"

# Perform backup
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
  --format=plain --no-owner --no-acl \
  | gzip > "${BACKUP_DIR}/daily/${BACKUP_FILE}"

echo "Backup completed: ${BACKUP_DIR}/daily/${BACKUP_FILE}"

# Monthly backup (on 1st of month)
if [ "$(date +%d)" = "01" ]; then
  cp "${BACKUP_DIR}/daily/${BACKUP_FILE}" "${BACKUP_DIR}/monthly/${BACKUP_FILE}"
  echo "Monthly backup created: ${BACKUP_DIR}/monthly/${BACKUP_FILE}"
fi

# Cleanup old backups
echo "Cleaning up old backups..."

# Remove daily backups older than RETENTION_DAYS
find "${BACKUP_DIR}/daily" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# Remove monthly backups older than RETENTION_MONTHS
find "${BACKUP_DIR}/monthly" -name "*.sql.gz" -mtime +$((RETENTION_MONTHS * 30)) -delete

echo "Backup retention applied: ${RETENTION_DAYS} days (daily), ${RETENTION_MONTHS} months (monthly)"

# Upload to S3/Azure (optional)
if [ -n "${S3_BUCKET}" ]; then
  echo "Uploading to S3: ${S3_BUCKET}"
  aws s3 cp "${BACKUP_DIR}/daily/${BACKUP_FILE}" "s3://${S3_BUCKET}/backups/postgresql/${BACKUP_FILE}"
fi

if [ -n "${AZURE_STORAGE_ACCOUNT}" ]; then
  echo "Uploading to Azure Blob Storage"
  az storage blob upload \
    --account-name "${AZURE_STORAGE_ACCOUNT}" \
    --container-name backups \
    --name "postgresql/${BACKUP_FILE}" \
    --file "${BACKUP_DIR}/daily/${BACKUP_FILE}"
fi

echo "Backup process completed successfully"

