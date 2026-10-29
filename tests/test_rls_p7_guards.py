"""RLS-Plan P7: Absicherung gegen Umgehung.

- Die Anwendungsverbindung darf RLS nicht umgehen (Superuser, BYPASSRLS, Eigentuemer); in
  Produktion verweigert der Start.
- Neue Engines/Verbindungen entstehen nur an freigegebenen Stellen.
- Sicherheitskern und RLS-Artefakte stehen unter Code-Owner-Review.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import sqlalchemy as sa

ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get("TEST_DATABASE_URL")

# Freigegebene Stellen fuer eigene Engines im Backend (Dienste unter services/* haben eigene).
ENGINE_ALLOWED = {
    "app/core/database.py",           # Anwendungs- und Systemverbindung
    "app/core/migration_session.py",  # Migrator
    "app/services/studio_process_simulation.py",  # Simulation gegen den Pruefstand
}


@pytest.mark.unit
def test_neue_engines_nur_an_freigegebenen_stellen():
    inventory = json.loads((ROOT / "docs" / "admin" / "rls-inventory.json").read_text(encoding="utf-8"))
    backend = {f for f in inventory["code_paths"]["new_engine"] if not f.startswith("services/")}
    assert backend <= ENGINE_ALLOWED, sorted(backend - ENGINE_ALLOWED)


@pytest.mark.unit
def test_treiberverbindungen_gibt_es_nicht():
    inventory = json.loads((ROOT / "docs" / "admin" / "rls-inventory.json").read_text(encoding="utf-8"))
    assert inventory["code_paths"]["driver_connect"] == {}


@pytest.mark.unit
def test_sicherheitskern_unter_code_owner_review():
    owners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    for pattern in ("/app/core/database.py", "/app/core/rls_*", "/app/core/tenant*", "/scripts/rls_*",
                    "/scripts/provision_db_roles.py", "/app/workers/base_worker.py", "/alembic/",
                    "/docs/admin/rls-*.json"):
        assert any(line.split()[0] == pattern for line in owners.splitlines()
                   if line.strip() and not line.startswith("#")), pattern


@pytest.mark.unit
def test_start_verweigert_produktion_ohne_wirksames_rls(monkeypatch):
    from app.core import rls_guard

    class _Conn:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class _Engine:
        def connect(self):
            return _Conn()

    monkeypatch.setattr(rls_guard, "rls_problems", lambda conn: ["valeo_dev ist Superuser"])
    with pytest.raises(RuntimeError, match="RLS UNWIRKSAM"):
        rls_guard.enforce_rls_effective(_Engine(), "production")
    assert rls_guard.enforce_rls_effective(_Engine(), "development") == ["valeo_dev ist Superuser"]
    monkeypatch.setattr(rls_guard, "rls_problems", lambda conn: [])
    assert rls_guard.enforce_rls_effective(_Engine(), "production") == []


@pytest.mark.integration
def test_rollenpruefung_gegen_die_datenbank():
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    from app.core.rls_guard import rls_problems
    engine = sa.create_engine(URL)
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            assert any("Superuser" in p for p in rls_problems(conn))  # Pruefstand: valeo_dev
            conn.execute(sa.text("SET LOCAL ROLE valeo_app"))
            assert rls_problems(conn) == []
            conn.execute(sa.text("RESET ROLE"))
            if conn.execute(sa.text("SELECT 1 FROM pg_roles WHERE rolname = 'valeo_system'")).scalar():
                conn.execute(sa.text("SET LOCAL ROLE valeo_system"))
                assert rls_problems(conn) == ["valeo_system hat BYPASSRLS"]
        finally:
            tx.rollback()
    engine.dispose()
