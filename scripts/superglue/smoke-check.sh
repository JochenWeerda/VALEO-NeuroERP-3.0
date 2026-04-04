#!/usr/bin/env bash
set -euo pipefail

api_url="${1:-http://localhost:3010/health}"
curl -fsS "${api_url}" >/dev/null
echo "superglue smoke ok"

