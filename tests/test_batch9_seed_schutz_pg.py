"""PostgreSQL-Gegenprobe fuer die Batch-9-Seed-Signaturen; nur TEMP-Tabellen."""
import importlib.util
import os
from pathlib import Path

import pytest
import sqlalchemy as sa


spec = importlib.util.spec_from_file_location(
    "batch9_seed_guard", Path(__file__).resolve().parents[1] / "alembic/versions/compliance_register_mandant_20261104.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# Unabhaengige Abschrift der urspruenglichen Seedwerte aus dem Git-Vorgaenger.
CASES = {
    "ops_compliance_items": ({"bereich": "Gewaesserschutz", "anforderung": "Gewaesserrandstreifen 5m", "erfuellt": True, "nachweis": "Feldprotokoll", "frist": "2026-12-31 00:00:00"}, "anforderung"),
    "ops_enni_meldungen": ({"typ": "DBE", "betrieb": "Landwirtschaft Mueller", "vvvo": "03-276-1234", "datum": "2026-01-15 00:00:00", "status": "bestaetigt", "naehrstoff_n": 180, "naehrstoff_p": 60, "naehrstoff_k": 120}, "vvvo"),
    "ops_qs_checks": ({"bereich": "Wareneingangskontrolle", "pruefpunkt": "Lieferschein-Pruefung", "erfuellt": True, "bemerkung": "Vollstaendig", "geprueft_am": "2026-02-10 00:00:00"}, "pruefpunkt"),
    "ops_zulassungen_register": ({"produkt": "Roundup PowerFlex", "typ": "PSM", "nummer": "024567-00", "behoerde": "BVL", "gueltig_bis": "2026-12-31 00:00:00", "status": "aktiv"}, "nummer"),
    "ops_sachkunde_register": ({"kunde": "Landwirtschaft Mueller", "kundennr": "K-10023", "nachweis_nr": "SK-NDS-2022-4567", "ausstellungsdatum": "2022-03-15 00:00:00", "gueltig_bis": "2025-03-15 00:00:00", "ausstellende_stelle": "LWK Niedersachsen", "status": "ablaufend"}, "nachweis_nr"),
    "ops_saatgut_nachbau": ({"betrieb": "Landwirtschaft Mueller", "sorte": "Weichweizen Eltan", "kultur": "Weichweizen", "flaeche": 45.5, "erntejahr": 2024, "gebuehr": 682.5, "status": "bezahlt"}, "sorte"),
    "ops_vvvo_register": ({"betriebsname": "Landwirtschaft Mueller", "vvvo": "03-276-123456", "bundesland": "Niedersachsen", "tierart": "Rind (Milch)", "status": "aktiv", "letzte_aktualisierung": "2026-01-15 00:00:00"}, "vvvo"),
    "ops_zertifikate": ({"art": "Bio-Zertifikat", "standard": "EU-Bio-Verordnung", "nummer": "BIO-2025-1234", "gueltig_bis": "2026-12-31 00:00:00", "audit": "2026-02-15 00:00:00", "status": "gueltig"}, "nummer"),
}
DISPO = {"artikel": "Weizen Premium", "artikel_id": "ART-001", "bestand": 120, "mindestbestand": 200, "bedarf": 80, "empfehlung": "Nachbestellen: 100 t", "prioritaet": "hoch"}
TIMES = {"frist", "datum", "geprueft_am", "gueltig_bis", "ausstellungsdatum", "letzte_aktualisierung", "audit"}
NUMBERS = {"naehrstoff_n", "naehrstoff_p", "naehrstoff_k", "flaeche", "erntejahr", "gebuehr", "bestand", "mindestbestand", "bedarf"}


def _create(conn, name, row):
    columns = []
    for key, value in row.items():
        typ = "timestamptz" if key in TIMES else "numeric" if key in NUMBERS else "boolean" if isinstance(value, bool) else "text"
        columns.append(f"{key} {typ}")
    conn.exec_driver_sql(f"CREATE TEMP TABLE {name} (marker text, {', '.join(columns)}) ON COMMIT DROP")


def _insert(conn, name, marker, row):
    cols = ["marker", *row]
    conn.execute(sa.text(f"INSERT INTO {name} ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})"), {"marker": marker, **row})


def test_seed_deletions_and_drop_guard_on_postgresql(monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL fuer gemeinsamen Pruefstand fehlt")
    assert sa.engine.make_url(url).database == "valeo_probe"
    engine = sa.create_engine(url, connect_args={"application_name": "agent:batch9-seed-schutz"})
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            conn.exec_driver_sql("SET LOCAL TIME ZONE 'UTC'")
            monkeypatch.setattr(m.op, "execute", lambda sql: conn.exec_driver_sql(str(sql)))
            for index, (table, (row, key)) in enumerate(CASES.items()):
                name = f"seed_guard_{index}"
                _create(conn, name, row)
                _insert(conn, name, "seed", row)
                # Jedes einzelne Geschaeftsfeld muss Teil der Signatur sein.
                for field in row:
                    changed = dict(row)
                    changed[field] = None
                    _insert(conn, name, f"null-{field}", changed)
                    changed = dict(row)
                    value = row[field]
                    changed[field] = ("2030-01-01 00:00:00" if field in TIMES else
                                      not value if isinstance(value, bool) else
                                      value + 1 if field in NUMBERS else value + "-GEAENDERT")
                    _insert(conn, name, f"changed-{field}", changed)
                changed = dict(row)
                changed[key] += "-GEAENDERT"
                _insert(conn, name, "changed-key", changed)
                signature = m.SEEDS['domain_ops.' + table]
                monkeypatch.setitem(m.SEEDS, 'pg_temp.' + name, signature)
                m._seed_loeschen(conn, 'pg_temp.' + name)
                remaining = set(conn.execute(sa.text(f"SELECT marker FROM {name}")).scalars())
                assert remaining == {f"null-{field}" for field in row} | {f"changed-{field}" for field in row} | {"changed-key"}
            _create(conn, "seed_guard_tenant", next(iter(CASES.values()))[0])
            conn.exec_driver_sql("ALTER TABLE seed_guard_tenant ADD COLUMN tenant_id text")
            _insert(conn, "seed_guard_tenant", "tenant-seed-like", next(iter(CASES.values()))[0])
            conn.exec_driver_sql("UPDATE seed_guard_tenant SET tenant_id = 'tenant-a'")
            monkeypatch.setitem(m.SEEDS, 'pg_temp.seed_guard_tenant', m.SEEDS['domain_ops.ops_compliance_items'])
            m._seed_loeschen(conn, 'pg_temp.seed_guard_tenant')
            assert conn.execute(sa.text("SELECT count(*) FROM seed_guard_tenant")).scalar_one() == 1
            # Beide ausgemusterten Tabellen duerfen mit vorhandenen Testzeilen weg;
            # SAVEPOINT belegt, dass der DROP zurueckgerollt werden kann.
            for name in ("seed_guard_disposition", "seed_guard_zertifikate_api"):
                _create(conn, name, DISPO)
                _insert(conn, name, "seed", DISPO)
                _insert(conn, name, "changed", dict(DISPO, bestand=121))
                _insert(conn, name, "null", dict(DISPO, artikel_id=None))
                conn.exec_driver_sql(f"CREATE TEMP VIEW {name}_view AS SELECT * FROM {name}")
                dependent = conn.begin_nested()
                with pytest.raises(sa.exc.DBAPIError):
                    m._entfernen(conn, "pg_temp." + name)
                dependent.rollback()
                assert conn.execute(sa.text(f"SELECT count(*) FROM {name}")).scalar_one() == 3
                conn.exec_driver_sql(f"DROP VIEW {name}_view")
                drop = conn.begin_nested()
                m._entfernen(conn, "pg_temp." + name)
                assert conn.execute(sa.text("SELECT to_regclass(:name)"), {"name": "pg_temp." + name}).scalar() is None
                drop.rollback()
                assert conn.execute(sa.text(f"SELECT count(*) FROM {name}")).scalar_one() == 3
                m._entfernen(conn, "pg_temp." + name)
                m._entfernen(conn, "pg_temp." + name)  # fehlende Tabelle ist idempotent
        finally:
            tx.rollback()
    engine.dispose()
