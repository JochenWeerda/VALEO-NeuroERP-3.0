"""Die Projektionsbuchhaltung steht vor dem ersten Abruf.

``domain_shared.process_projection_registry``, ``.process_projection_snapshots``
und ``.process_projection_cursors`` wurden bis zum 30.09.2026 zur Laufzeit
angelegt — an zwei Stellen, fuer die Cursor-Tabelle doppelt. Auf einer frischen
Installation gab es sie erst, nachdem jemand eine Finanz-Projektion abgerufen
hatte.

Fuenf Vertraege:

1. Die drei Tabellen existieren nach ``alembic upgrade head``.
2. Ihre Form ist die der entfernten Laufzeit-DDL — Spalten, Typen, Nullbarkeit
   und Primaerschluessel woertlich.
3. Die Schreibpfade kommen ohne Laufzeit-DDL aus.
4. Im Anwendungspfad legt niemand mehr eine dieser Tabellen an.
5. Ein Lesefehler laesst keine abgebrochene Transaktion zurueck — das Muster,
   das am 29.09. eine DSGVO-Loeschung stillschweigend nichts tun liess.

Der Pruefstand ist eine **frisch migrierte** Datenbank. Ohne erreichbare
Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)

TABELLEN = (
    "process_projection_registry",
    "process_projection_snapshots",
    "process_projection_cursors",
)

# Woertlich aus der entfernten Laufzeit-DDL: Name -> (Datentyp, nullbar).
# Die Zeitstempel sind bewusst ``text``: Der Lesepfad vergleicht sie als
# Zeichenketten, um den juengsten Stand zu finden.
FORM: dict[str, dict[str, tuple[str, bool]]] = {
    "process_projection_registry": {
        "tenant_id": ("text", False),
        "projection_key": ("text", False),
        "item_count": ("integer", False),
        "last_rebuilt_at": ("text", True),
        "last_accessed_at": ("text", True),
        "updated_at": ("text", False),
    },
    "process_projection_snapshots": {
        "tenant_id": ("text", False),
        "projection_key": ("text", False),
        "schema_version": ("integer", False),
        "item_count": ("integer", False),
        "payload": ("text", False),
        "rebuilt_at": ("text", False),
        "updated_at": ("text", False),
    },
    "process_projection_cursors": {
        "tenant_id": ("text", False),
        "consumer_id": ("text", False),
        "projection_key": ("text", False),
        "schema_version": ("integer", False),
        "cursor_token": ("text", True),
        "last_event_id": ("text", True),
        "source_rebuilt_at": ("text", True),
        "replay_from_event_id": ("text", True),
        "replay_to_event_id": ("text", True),
        "status": ("text", False),
        "updated_at": ("text", False),
    },
}

SCHLUESSEL = {
    "process_projection_registry": ["tenant_id", "projection_key"],
    "process_projection_snapshots": ["tenant_id", "projection_key"],
    "process_projection_cursors": ["tenant_id", "consumer_id", "projection_key"],
}


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_shared.process_projection_cursors')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration projektion_cursor_20260930 nicht angewandt")
    return motor


@pytest.fixture()
def mandant() -> str:
    return f"test-{uuid.uuid4().hex[:8]}"


# 1 + 2 -- Form ---------------------------------------------------------------

@pytest.mark.parametrize("tabelle", TABELLEN)
def test_tabelle_hat_die_form_der_entfernten_laufzeit_ddl(engine, tabelle):
    from sqlalchemy import text

    with engine.connect() as conn:
        zeilen = conn.execute(
            text(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'domain_shared' AND table_name = :t
                """
            ),
            {"t": tabelle},
        ).mappings().all()

    ist = {z["column_name"]: (z["data_type"], z["is_nullable"] == "YES") for z in zeilen}
    assert ist == FORM[tabelle], f"{tabelle} weicht von der Laufzeit-DDL ab"


@pytest.mark.parametrize("tabelle", TABELLEN)
def test_primaerschluessel_traegt_den_mandanten_vorn(engine, tabelle):
    from sqlalchemy import text

    with engine.connect() as conn:
        spalten = [
            z[0]
            for z in conn.execute(
                text(
                    """
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a
                      ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = ('domain_shared.' || :t)::regclass
                      AND i.indisprimary
                    ORDER BY array_position(i.indkey, a.attnum)
                    """
                ),
                {"t": tabelle},
            ).all()
        ]

    assert spalten == SCHLUESSEL[tabelle]
    # Jede Abfrage filtert nach tenant_id. Steht der Mandant vorn, braucht es
    # keinen zusaetzlichen Index.
    assert spalten[0] == "tenant_id"


# 3 -- Schreiben ohne Laufzeit-DDL --------------------------------------------

def test_cursor_wird_ohne_bootstrap_geschrieben(engine, mandant):
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    from app.core.projection_cursor_service import persist_projection_cursor

    with Session(engine) as db:
        persist_projection_cursor(
            db,
            mandant,
            "finance-projections-01",
            "ap-invoice-cockpit",
            last_event_id="evt-1",
        )

    with engine.connect() as conn:
        zeile = conn.execute(
            text(
                "SELECT status, last_event_id, schema_version "
                "FROM domain_shared.process_projection_cursors WHERE tenant_id = :t"
            ),
            {"t": mandant},
        ).mappings().one()
    assert zeile["status"] == "active"
    assert zeile["last_event_id"] == "evt-1"
    assert zeile["schema_version"] == 1


def test_register_und_abbild_ohne_bootstrap_geschrieben(engine, mandant):
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    from app.api.v1.schemas.finance_read_models_schemas import ProjectionStatusReadModel
    from app.services.finance_read_model_service import (
        persist_projection_registry_entry,
        persist_projection_snapshot,
    )

    with Session(engine) as db:
        persist_projection_registry_entry(
            db, mandant, "ap-invoice-cockpit", 7, rebuilt_at="2026-09-30T10:00:00+00:00"
        )
        persist_projection_snapshot(
            db,
            mandant,
            "ap-invoice-cockpit",
            ProjectionStatusReadModel(tenant_id=mandant),
            rebuilt_at="2026-09-30T10:00:00+00:00",
        )

    with engine.connect() as conn:
        register = conn.execute(
            text(
                "SELECT item_count FROM domain_shared.process_projection_registry "
                "WHERE tenant_id = :t AND projection_key = 'ap-invoice-cockpit'"
            ),
            {"t": mandant},
        ).scalar()
        abbild = conn.execute(
            text(
                "SELECT count(*) FROM domain_shared.process_projection_snapshots "
                "WHERE tenant_id = :t"
            ),
            {"t": mandant},
        ).scalar()
    assert register == 7
    assert abbild == 1


# 4 -- Keine Laufzeit-DDL mehr im Anwendungspfad ------------------------------

def test_anwendungspfad_legt_die_tabellen_nicht_mehr_an():
    wurzel = Path(__file__).resolve().parents[1]
    funde: list[str] = []
    for verzeichnis in ("app", "modules"):
        for pfad in (wurzel / verzeichnis).rglob("*.py"):
            inhalt = pfad.read_text(encoding="utf-8", errors="ignore")
            if "CREATE TABLE" not in inhalt:
                continue
            for tabelle in TABELLEN:
                if f"CREATE TABLE IF NOT EXISTS domain_shared.{tabelle}" in inhalt:
                    funde.append(f"{pfad.relative_to(wurzel)} -> {tabelle}")
    assert not funde, "Laufzeit-DDL wieder eingefuehrt: " + ", ".join(funde)


# 5 -- Ein Lesefehler laesst keine tote Transaktion zurueck -------------------

def test_lesefehler_gibt_die_transaktion_frei(engine, mandant):
    """Die Spalte, die gelesen wird, wird kurzzeitig umbenannt.

    Vorher: Das ``except`` fing den Fehler, die Transaktion blieb abgebrochen,
    und jede weitere Abfrage derselben Anfrage scheiterte mit
    ``InFailedSqlTransaction`` — sichtbar wurde davon nichts.
    """
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    from app.services.finance_read_model_service import (
        _load_persisted_projection_registry,
    )

    with engine.begin() as v:
        v.execute(
            text(
                "ALTER TABLE domain_shared.process_projection_registry "
                "RENAME COLUMN item_count TO item_count_weg"
            )
        )
    try:
        with Session(engine) as db:
            eintraege, zuletzt = _load_persisted_projection_registry(
                db=db, tenant_id=mandant
            )
            assert eintraege == {}
            assert zuletzt is None
            # Der Beweis: dieselbe Sitzung ist weiter benutzbar.
            assert db.execute(text("SELECT 1")).scalar() == 1
    finally:
        with engine.begin() as v:
            v.execute(
                text(
                    "ALTER TABLE domain_shared.process_projection_registry "
                    "RENAME COLUMN item_count_weg TO item_count"
                )
            )
