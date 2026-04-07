#!/usr/bin/env bash
set -euo pipefail

TENANT_ID="${1:-default}"
FORMAT="${2:-json}"
OUTPUT_PATH="${3:-}"

ARGS=(scripts/superglue/export-onboarding-pack.py --tenant "$TENANT_ID" --format "$FORMAT")
if [[ -n "$OUTPUT_PATH" ]]; then
  ARGS+=(--output "$OUTPUT_PATH")
fi

if command -v python3 >/dev/null 2>&1; then
  python3 "${ARGS[@]}"
elif command -v python >/dev/null 2>&1; then
  python "${ARGS[@]}"
else
  echo "python3/python not found" >&2
  exit 1
fi
