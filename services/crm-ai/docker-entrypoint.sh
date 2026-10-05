#!/bin/sh
# A failed migration must prevent a healthy-looking service from starting.
set -eu
alembic upgrade head
exec uvicorn main:app --host 0.0.0.0 --port 6200
