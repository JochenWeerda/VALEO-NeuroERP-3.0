import os
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
import sqlalchemy as sa


SPEC = importlib.util.spec_from_file_location("batch8_migration_guard", Path(__file__).resolve().parents[1] / "alembic/versions/scheinwege_mandant_20261103.py")
migration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(migration)


@pytest.fixture
def bind(monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL fuer gemeinsamen Pruefstand fehlt")
    engine = sa.create_engine(url, connect_args={"application_name": "agent:batch8-seed-schutz"})
    with engine.connect() as conn:
        tx = conn.begin()
        monkeypatch.setattr(migration, "MARKETING", "batch8_marketing")
        monkeypatch.setattr(migration, "FOERDER", "batch8_foerder")
        monkeypatch.setattr(migration, "PROBEN", "batch8_proben")
        monkeypatch.setattr(migration, "AUFTRAEGE", "batch8_auftraege")
        monkeypatch.setattr(migration, "_exists", lambda _bind, _table: True)
        monkeypatch.setattr(migration, "_has_column", lambda _bind, _table, _column: False)
        monkeypatch.setattr(migration, "op", SimpleNamespace(execute=lambda sql: conn.execute(sa.text(sql))))
        try:
            yield conn
        finally:
            tx.rollback()
    engine.dispose()


def test_marketing_seed_vollstaendig_und_fremde_zeilen_blockieren(bind):
    bind.exec_driver_sql("CREATE TEMP TABLE batch8_marketing (name text, typ text, zielgruppe text, startdatum timestamptz, enddatum timestamptz, budget numeric, status text)")
    seed = ("Herbst-Aktion Weizen", "E-Mail", "Landwirte", "2025-10-01 00:00:00", "2025-10-31 00:00:00", 2500, "beendet")
    insert = "INSERT INTO batch8_marketing VALUES (%s, %s, %s, %s, %s, %s, %s)"
    for changed in (seed[:5] + (2501, seed[6]), (None,) + seed[1:], seed[:2] + (None,) + seed[3:]):
        bind.exec_driver_sql(insert, changed)
        with pytest.raises(RuntimeError):
            migration._marketing_entfernen(bind)
        assert bind.exec_driver_sql("SELECT count(*) FROM batch8_marketing").scalar() == 1
        bind.exec_driver_sql("DELETE FROM batch8_marketing")
    bind.exec_driver_sql(insert, seed)
    bind.exec_driver_sql(insert, seed)
    with pytest.raises(RuntimeError):
        migration._marketing_entfernen(bind)
    assert bind.exec_driver_sql("SELECT count(*) FROM batch8_marketing").scalar() == 2
    bind.exec_driver_sql("DELETE FROM batch8_marketing")
    bind.exec_driver_sql(insert, seed)
    bind.exec_driver_sql(insert, ("Fruehjahrs-Duenger-Kampagne", "Newsletter", "Ackerbau", "2026-02-15 00:00:00", "2026-03-31 00:00:00", 3000, "aktiv"))
    migration._marketing_entfernen(bind)
    assert bind.exec_driver_sql("SELECT to_regclass('pg_temp.batch8_marketing')").scalar() is None


def test_nur_vollstaendige_foerder_und_labor_seeds_werden_entfernt(bind):
    bind.exec_driver_sql("CREATE TEMP TABLE batch8_foerder (nummer text, programm text, antragsdatum timestamptz, flaeche numeric, betrag numeric, status text)")
    bind.exec_driver_sql("CREATE TEMP TABLE batch8_proben (id text, probennummer text, typ text, artikel text, datum timestamptz, labor text, status text)")
    bind.exec_driver_sql("CREATE TEMP TABLE batch8_auftraege (id text, chargen_id text, labor text, analysen integer, auftragsdatum timestamptz, status text)")
    bind.exec_driver_sql("INSERT INTO batch8_foerder VALUES ('FA-2026-001','Greening','2026-03-15 00:00:00',250,21250,'bewilligt'), ('FA-2026-002','Junglandwirte','2026-04-01 00:00:00',120,15000,'geändert')")
    bind.exec_driver_sql("INSERT INTO batch8_proben VALUES ('LB-SEED-2026-001','LB-2026-001','Qualitaetspruefung','Weizen Premium','2026-02-10 00:00:00','Lufa Nord-West','abgeschlossen'), ('LB-SEED-2026-002','LB-2026-002','Rueckstandsanalyse','Raps','2026-02-11 00:00:00','SGS',NULL), ('real','BEF-LA-SEED-WEI-001','Laborbefund','x','2026-02-10 00:00:00','Lufa Nord-West','freigeben')")
    bind.exec_driver_sql("INSERT INTO batch8_auftraege VALUES ('LA-SEED-WEI-001','251011-WEI-001','Lufa Nord-West',4,'2026-02-10 00:00:00','in-bearbeitung'), ('LA-SEED-RAP-002','251010-RAP-002','SGS',7,'2026-02-09 00:00:00','abgeschlossen'), ('test','TEST-CHARGE-001','Test-Labor',1,'2026-02-09 00:00:00','offen')")
    migration._seed_loeschen(bind)
    assert bind.exec_driver_sql("SELECT nummer FROM batch8_foerder").scalars().all() == ['FA-2026-002']
    assert set(bind.exec_driver_sql("SELECT id FROM batch8_proben").scalars()) == {'LB-SEED-2026-002', 'real'}
    assert set(bind.exec_driver_sql("SELECT id FROM batch8_auftraege").scalars()) == {'LA-SEED-RAP-002', 'test'}
