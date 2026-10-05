#!/usr/bin/env bash
# Lokaler Erntepeak-Lasttest (SPEC-P1-10) gegen docker-compose / localhost.
set -euo pipefail

PROFILE="${1:-local}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
API_DEV_TOKEN="${API_DEV_TOKEN:-dev-token}"
TENANT_ID="${TENANT_ID:-00000000-0000-0000-0000-000000000001}"
READY_TIMEOUT_SEC="${READY_TIMEOUT_SEC:-90}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if ! command -v k6 >/dev/null 2>&1; then
  echo "k6 fehlt. Installation: https://k6.io/docs/get-started/installation/" >&2
  exit 1
fi

echo "Warte auf Backend unter ${BASE_URL}..."
deadline=$((SECONDS + READY_TIMEOUT_SEC))
ready=0
while (( SECONDS < deadline )); do
  for path in /healthz /health/live /api/v1/status; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "${BASE_URL}${path}" || true)
    if [[ "$code" =~ ^[23] ]]; then
      echo "OK: ${BASE_URL}${path} -> ${code}"
      ready=1
      break
    fi
  done
  (( ready == 1 )) && break
  sleep 2
done

if (( ready != 1 )); then
  echo "Backend nicht erreichbar unter ${BASE_URL}." >&2
  exit 1
fi

mkdir -p reports/performance
SUMMARY="reports/performance/harvest-peak-${PROFILE}-summary.json"

echo "Starte k6 PROFILE=${PROFILE} gegen ${BASE_URL}"
k6 run \
  --env "PROFILE=${PROFILE}" \
  --env "BASE_URL=${BASE_URL}" \
  --env "API_DEV_TOKEN=${API_DEV_TOKEN}" \
  --env "TENANT_ID=${TENANT_ID}" \
  --summary-export "${SUMMARY}" \
  tests/load/harvest-peak.js

echo "Fertig. Summary: ${SUMMARY}"
