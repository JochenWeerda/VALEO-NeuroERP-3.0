"""Schutz-Migration: echte Altrechnungen ausserhalb DocFlow halten das Entfernen des alten Rechnungswegs an."""
from __future__ import annotations

import importlib.util
import json
import os
import uuid
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

pytestmark = pytest.mark.integration

WURZEL = Path(__file__).resolve().parents[1]
DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


def _pruefe(verbindung) -> None:
    spec = importlib.util.spec_from_file_location("m", WURZEL / "alembic/versions/altrechnungen_schutz_20261110.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    with Operations.context(MigrationContext.configure(verbindung)):
        modul.upgrade()


@pytest.fixture
def verbindung():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5})
        conn = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    tx = conn.begin()
    try:
        yield conn
    finally:
        tx.rollback()
        conn.close()


def _altrechnung(verbindung, mandant: str) -> None:
    verbindung.execute(sa.text("INSERT INTO public.documents (id, doc_type, doc_number, data) "
                               "VALUES (:id, 'sales_invoice', :nr, CAST(:d AS jsonb))"),
                       {"id": str(uuid.uuid4()), "nr": f"RE-ALT-{uuid.uuid4().hex[:6]}",
                        "d": json.dumps({"tenantId": mandant, "status": "GEBUCHT"})})


def test_testreste_ohne_mandant_halten_nicht_an(verbindung):
    _altrechnung(verbindung, f"test-{uuid.uuid4().hex[:8]}")
    _pruefe(verbindung)


def test_altrechnung_eines_bestehenden_mandanten_haelt_an(verbindung):
    mandant = f"ar-{uuid.uuid4().hex[:8]}"
    verbindung.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"),
                       {"t": mandant})
    _altrechnung(verbindung, mandant)
    with pytest.raises(RuntimeError, match="erst uebernehmen"):
        _pruefe(verbindung)
