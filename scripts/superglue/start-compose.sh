#!/usr/bin/env bash
set -euo pipefail

: "${SUPERGLUE_DB_PASSWORD:?SUPERGLUE_DB_PASSWORD is required}"
: "${SUPERGLUE_AUTH_TOKEN:?SUPERGLUE_AUTH_TOKEN is required}"
: "${SUPERGLUE_MINIO_ROOT_PASSWORD:?SUPERGLUE_MINIO_ROOT_PASSWORD is required}"

docker compose -f docker-compose.integration.yml --profile superglue up -d "$@"

