#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${SUPERGLUE_CI_BASE_URL:-}" && -n "${GITHUB_ACTIONS:-}" ]]; then
  echo "SUPERGLUE_CI_BASE_URL not configured; skipping external Superglue CI smoke."
  exit 0
fi

BASE_URL="${SUPERGLUE_CI_BASE_URL:-${SUPERGLUE_BASE_URL:-http://localhost:3011}}"
TENANT_ID="${SUPERGLUE_CI_TENANT_ID:-ci-tenant}"

echo "Superglue CI smoke against ${BASE_URL} for tenant ${TENANT_ID}"
curl -fsS "${BASE_URL%/}/v1/health" >/dev/null
curl -fsS "${BASE_URL%/}/v1/tools?page=1&limit=100" >/dev/null
echo "Superglue CI smoke passed"
