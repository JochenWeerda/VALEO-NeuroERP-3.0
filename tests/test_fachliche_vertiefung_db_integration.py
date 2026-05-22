"""Opt-in DB-Gate fuer fachliche Vertiefung Wave 10-13.

Dieser Test laeuft nur mit RUN_DB_INTEGRATION=1 und einer echten PostgreSQL-URL.
Er prueft den repo-seitig kritischen Pfad: `alembic upgrade head`, zentrale
Wave-10-13-Tabellen und eine transaktionale Warengruppen-Hierarchie.
"""
from __future__ import annotations

import os
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text


pytestmark = pytest.mark.integration


def _database_url() -> str:
    return (
        os.environ.get("DATABASE_URL")
        or os.environ.get("ERP_DATABASE_URL")
        or os.environ.get("CRM_DATABASE_URL")
        or ""
    )


def _require_db_gate() -> str:
    if os.environ.get("RUN_DB_INTEGRATION") != "1":
        pytest.skip("DB-Gate deaktiviert: RUN_DB_INTEGRATION=1 setzen.")
    url = _database_url()
    if not url:
        pytest.fail("DB-Gate benoetigt DATABASE_URL, ERP_DATABASE_URL oder CRM_DATABASE_URL.")
    return url


def test_alembic_upgrade_head_and_wave_tables_exist() -> None:
    database_url = _require_db_gate()
    env = {**os.environ, "DATABASE_URL": database_url}

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        text=True,
        capture_output=True,
        env=env,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    required_tables = [
        "domain_shared.hauptwarengruppen",
        "domain_shared.oberwarengruppen",
        "domain_shared.warengruppen",
        "domain_shared.erloeskennziffern",
        "domain_shared.zahlungsbedingungen",
        "domain_shared.partiestamm",
        "domain_shared.forderungsgruppen",
        "domain_shared.zu_abschlaggruppen",
        "domain_shared.zahlungsformulare",
        "domain_shared.zinsgruppen",
        "domain_shared.leergutarten",
    ]

    with engine.connect() as conn:
        existing = {
            table_name: conn.execute(
                text("SELECT to_regclass(:table_name)"),
                {"table_name": table_name},
            ).scalar()
            for table_name in required_tables
        }

    missing = [table for table, regclass in existing.items() if regclass is None]
    assert missing == []


def test_warengruppen_roundtrip_is_transactional() -> None:
    database_url = _require_db_gate()
    engine = create_engine(database_url)
    tenant_id = f"gate-{uuid4()}"
    suffix = uuid4().hex[:8]
    haupt_id = f"hwg-{suffix}"
    ober_id = f"owg-{suffix}"
    waren_id = f"wg-{suffix}"

    with engine.connect() as conn:
        tx = conn.begin()
        try:
            conn.execute(
                text("""
                    INSERT INTO domain_shared.hauptwarengruppen
                        (id, tenant_id, gruppe_nr, bezeichnung)
                    VALUES (:id, :tenant_id, :nr, :bezeichnung)
                """),
                {
                    "id": haupt_id,
                    "tenant_id": tenant_id,
                    "nr": f"HG-{suffix}",
                    "bezeichnung": "Gate Hauptwarengruppe",
                },
            )
            conn.execute(
                text("""
                    INSERT INTO domain_shared.oberwarengruppen
                        (id, tenant_id, gruppe_nr, bezeichnung, haupt_id)
                    VALUES (:id, :tenant_id, :nr, :bezeichnung, :haupt_id)
                """),
                {
                    "id": ober_id,
                    "tenant_id": tenant_id,
                    "nr": f"OG-{suffix}",
                    "bezeichnung": "Gate Oberwarengruppe",
                    "haupt_id": haupt_id,
                },
            )
            conn.execute(
                text("""
                    INSERT INTO domain_shared.warengruppen
                        (id, tenant_id, gruppe_nr, bezeichnung, ober_id)
                    VALUES (:id, :tenant_id, :nr, :bezeichnung, :ober_id)
                """),
                {
                    "id": waren_id,
                    "tenant_id": tenant_id,
                    "nr": f"WG-{suffix}",
                    "bezeichnung": "Gate Warengruppe",
                    "ober_id": ober_id,
                },
            )
            conn.execute(
                text("""
                    UPDATE domain_shared.warengruppen
                    SET bezeichnung = :bezeichnung
                    WHERE tenant_id = :tenant_id AND id = :id
                """),
                {
                    "bezeichnung": "Gate Warengruppe aktualisiert",
                    "tenant_id": tenant_id,
                    "id": waren_id,
                },
            )
            value = conn.execute(
                text("""
                    SELECT wg.bezeichnung
                    FROM domain_shared.warengruppen wg
                    JOIN domain_shared.oberwarengruppen owg ON owg.id = wg.ober_id
                    JOIN domain_shared.hauptwarengruppen hwg ON hwg.id = owg.haupt_id
                    WHERE wg.tenant_id = :tenant_id AND wg.id = :id
                """),
                {"tenant_id": tenant_id, "id": waren_id},
            ).scalar_one()
            assert value == "Gate Warengruppe aktualisiert"
        finally:
            tx.rollback()
