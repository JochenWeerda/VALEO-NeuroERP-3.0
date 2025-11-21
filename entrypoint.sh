#!/usr/bin/env bash
set -e

echo "🔄 Warte auf PostgreSQL..."

# Warte auf DB (mit psycopg2 - SYNC)
python - <<'PY'
import psycopg2
import os
import time

# DATABASE_URL parsen: postgresql://user:pass@host:port/db
db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/valeo")
db_url = db_url.replace("postgresql://", "")

try:
    user_pass, host_db = db_url.split("@")
    user, password = user_pass.split(":")
    host_port, dbname = host_db.split("/")
    host = host_port.split(":")[0] if ":" in host_port else host_port
    port = host_port.split(":")[1] if ":" in host_port else "5432"
    
    for i in range(30):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            version = conn.fetchone()[0] if conn else "unknown"
            conn.close()
            print(f"✅ PostgreSQL ready! (Attempt {i+1})")
            break
        except Exception as e:
            print(f"⏳ DB not ready yet (attempt {i+1}/30): {e}")
            time.sleep(1)
    else:
        print("❌ DB not reachable after 30s")
        exit(1)
except Exception as e:
    print(f"❌ Error parsing DATABASE_URL: {e}")
    exit(1)
PY

echo "📦 Führe Alembic Migrations aus..."
if [ -f "alembic.ini" ]; then
  alembic upgrade head || echo "⚠️ Alembic failed, continuing..."
fi

echo "🚀 Starte Backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload

