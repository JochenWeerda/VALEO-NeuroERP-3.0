#!/usr/bin/env bash
set -euo pipefail

backup_dir="${1:-runtime/superglue-backups}"
mkdir -p "${backup_dir}/db"

docker compose -f docker-compose.integration.yml exec -T superglue-db \
  pg_dump -U "${SUPERGLUE_DB_USER:-superglue}" -d "${SUPERGLUE_DB_NAME:-superglue}" -Fc \
  > "${backup_dir}/db/superglue_$(date +%Y%m%d_%H%M%S).dump"

echo "db backup written to ${backup_dir}/db"

