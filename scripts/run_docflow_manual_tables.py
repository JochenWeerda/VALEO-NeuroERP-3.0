"""
Führt scripts/sql/docflow_manual_create_tables.sql aus (legt domain_docflow-Tabellen an).
Verwendet DATABASE_URL aus Umgebung/.env. Danach: alembic upgrade head
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, text
from app.core.config import settings


def main() -> None:
    sql_path = PROJECT_ROOT / "scripts" / "sql" / "docflow_manual_create_tables.sql"
    if not sql_path.exists():
        raise SystemExit(f"SQL-Datei nicht gefunden: {sql_path}")
    sql = sql_path.read_text(encoding="utf-8")
    # Zeilen die nur Kommentare/leer sind entfernen, dann nach ; trennen
    lines = []
    for line in sql.splitlines():
        s = line.strip()
        if s and not s.startswith("--"):
            lines.append(line)
        elif not s:
            lines.append("")
    sql_clean = "\n".join(lines)
    statements = [s.strip() for s in sql_clean.split(";") if s.strip()]
    engine = create_engine(settings.DATABASE_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_docflow"))
        for stmt in statements:
            if not stmt:
                continue
            try:
                conn.execute(text(stmt))
            except Exception as e:
                print(f"Warnung bei Statement: {e}")
                raise
    print("Docflow-Tabellen (domain_docflow) angelegt.")


if __name__ == "__main__":
    main()
