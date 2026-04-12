#!/usr/bin/env sh
set -eu

CONTAINER_NAME="${1:-valeo-first-install-smoke}"
HOST_PORT="${HOST_PORT:-55432}"

docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker run --name "$CONTAINER_NAME" \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=valeo_test \
  -p "${HOST_PORT}:5432" \
  -d postgres:15 >/dev/null

cleanup() {
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

i=0
while [ "$i" -lt 40 ]; do
  if docker exec "$CONTAINER_NAME" pg_isready -U postgres -d valeo_test >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 2
done

export DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:${HOST_PORT}/valeo_test"
python scripts/init_db.py
python scripts/check_required_domain_schemas.py
python scripts/check_domain_table_ownership.py
echo "First-install smoke passed."
