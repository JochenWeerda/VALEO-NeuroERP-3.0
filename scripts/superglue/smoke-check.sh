#!/usr/bin/env bash
set -euo pipefail

api_url="${1:-http://localhost:3011/v1/health}"
tools_url="${2:-http://localhost:3011/v1/tools}"
max_attempts="${SUPERGLUE_SMOKE_MAX_ATTEMPTS:-20}"
delay_seconds="${SUPERGLUE_SMOKE_DELAY_SECONDS:-2}"

for ((attempt=1; attempt<=max_attempts; attempt++)); do
  if curl -fsS "${api_url}" >/dev/null; then
    if [[ -n "${SUPERGLUE_AUTH_TOKEN:-}" ]]; then
      curl -fsS -H "Authorization: Bearer ${SUPERGLUE_AUTH_TOKEN}" "${tools_url}" >/dev/null
    fi
    echo "superglue smoke ok"
    exit 0
  fi
  if [[ "${attempt}" -lt "${max_attempts}" ]]; then
    sleep "${delay_seconds}"
  fi
done

curl -fsS "${api_url}" >/dev/null
if [[ -n "${SUPERGLUE_AUTH_TOKEN:-}" ]]; then
  curl -fsS -H "Authorization: Bearer ${SUPERGLUE_AUTH_TOKEN}" "${tools_url}" >/dev/null
fi
echo "superglue smoke ok"
