#!/usr/bin/env bash
set -euo pipefail

dump_file="${1:?dump file is required}"
cat "${dump_file}" | docker compose -f docker-compose.integration.yml exec -T superglue-db \
  pg_restore -U "${SUPERGLUE_DB_USER:-superglue}" -d "${SUPERGLUE_DB_NAME:-superglue}" --clean --if-exists

echo "db restore completed"

