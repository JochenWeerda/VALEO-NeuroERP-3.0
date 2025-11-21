#!/usr/bin/env sh
set -e

# Run Alembic migrations if DB is configured
if [ -n "${INVENTORY_DATABASE_URL}" ]; then
  echo "Running Alembic migrations..."
  alembic -c /app/alembic.ini upgrade head || {
    echo "Alembic migrations failed"; exit 1;
  }
else
  echo "INVENTORY_DATABASE_URL not set, skipping migrations."
fi

exec "$@"


