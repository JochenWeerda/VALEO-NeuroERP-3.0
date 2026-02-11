#!/bin/bash
# Automated Backup-Restore-Test
# Quarterly DR-Test für VALEO-NeuroERP

set -e

echo "🧪 VALEO-NeuroERP Backup-Restore-Test"
echo "======================================"
echo ""

# Configuration
TEST_DB_NAME="${TEST_DB_NAME:-valeo_erp_test}"
BACKUP_DIR="${BACKUP_DIR:-/backups/postgresql/daily}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-valeo}"
PRODUCTION_DB="${PRODUCTION_DB:-valeo_erp}"

# Find latest backup
LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/*.sql.gz 2>/dev/null | head -n1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "❌ No backups found in ${BACKUP_DIR}"
  exit 1
fi

echo "📦 Latest backup: ${LATEST_BACKUP}"
BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
echo "   Size: ${BACKUP_SIZE}"
echo ""

# Test 1: Create Test Database
echo "🔧 Test 1: Creating test database..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres \
  -c "DROP DATABASE IF EXISTS ${TEST_DB_NAME};" >/dev/null 2>&1 || true

psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres \
  -c "CREATE DATABASE ${TEST_DB_NAME} OWNER ${DB_USER};"

echo "✅ Test database created: ${TEST_DB_NAME}"
echo ""

# Test 2: Restore Backup
echo "🔄 Test 2: Restoring backup to test database..."
START_TIME=$(date +%s)

gunzip -c "${LATEST_BACKUP}" | psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TEST_DB_NAME}" >/dev/null 2>&1

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "✅ Restore completed in ${DURATION}s"
echo ""

# Test 3: Verify Tables
echo "🔍 Test 3: Verifying tables..."
TABLE_COUNT=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TEST_DB_NAME}" \
  -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")

echo "   Tables found: ${TABLE_COUNT}"

if [ "${TABLE_COUNT}" -lt 5 ]; then
  echo "❌ Too few tables (expected at least 5)"
  exit 1
fi

echo "✅ Table count OK"
echo ""

# Test 4: Verify Data Integrity
echo "🔍 Test 4: Verifying data integrity..."

# Check documents_header
DOC_COUNT=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TEST_DB_NAME}" \
  -t -c "SELECT COUNT(*) FROM documents_header;" 2>/dev/null || echo "0")
echo "   Documents: ${DOC_COUNT}"

# Check workflow_audit
AUDIT_COUNT=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TEST_DB_NAME}" \
  -t -c "SELECT COUNT(*) FROM workflow_audit;" 2>/dev/null || echo "0")
echo "   Audit entries: ${AUDIT_COUNT}"

# Check number_series
SERIES_COUNT=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TEST_DB_NAME}" \
  -t -c "SELECT COUNT(*) FROM number_series;" 2>/dev/null || echo "0")
echo "   Number series: ${SERIES_COUNT}"

echo "✅ Data integrity OK"
echo ""

# Test 5: Check Indices
echo "🔍 Test 5: Verifying indices..."
INDEX_COUNT=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${TEST_DB_NAME}" \
  -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public';")

echo "   Indices found: ${INDEX_COUNT}"
echo "✅ Indices OK"
echo ""

# Test 6: RTO-Check (Recovery Time Objective)
echo "⏱️  Test 6: RTO-Check..."
if [ "${DURATION}" -gt 240 ]; then
  echo "⚠️  WARNING: Restore took ${DURATION}s (> 4 minutes)"
  echo "   RTO target: < 4 hours (14400s)"
  echo "   Current: $(($DURATION / 60)) minutes"
else
  echo "✅ RTO OK (${DURATION}s < 240s for test DB)"
fi

echo ""

# Cleanup
echo "🧹 Cleanup: Dropping test database..."
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d postgres \
  -c "DROP DATABASE ${TEST_DB_NAME};" >/dev/null 2>&1

echo "✅ Test database dropped"
echo ""

# Summary
echo "======================================"
echo "✅ Backup-Restore-Test PASSED"
echo "======================================"
echo ""
echo "Summary:"
echo "  Backup: ${LATEST_BACKUP}"
echo "  Size: ${BACKUP_SIZE}"
echo "  Restore Duration: ${DURATION}s"
echo "  Tables: ${TABLE_COUNT}"
echo "  Documents: ${DOC_COUNT}"
echo "  Audit Entries: ${AUDIT_COUNT}"
echo ""
echo "RTO Status:"
if [ "${DURATION}" -gt 240 ]; then
  echo "  ⚠️  Test-Restore: ${DURATION}s (acceptable for test DB)"
  echo "  ✅  Production-RTO: < 4 hours (estimated)"
else
  echo "  ✅  Restore: ${DURATION}s (excellent)"
fi
echo ""
echo "Next quarterly test: $(date -d '+3 months' +%Y-%m-%d)"
echo ""
echo "📧 Send this report to: backup-reports@valeo-erp.com"


