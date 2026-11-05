"""Echte PostgreSQL-Praedikate auf TEMP-Daten; kein JWT-/RLS-Nachweis."""
import os
from datetime import date

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.services.compliance_vvvo_sachkunde_service import (
    VVVOError, berechne_naechste_vvvo_pruefung, get_sachkunde_status,
)


@pytest.fixture
def daten():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL fuer vorhandenen Pruefstand fehlt")
    parsed = sa.engine.make_url(url)
    assert parsed.get_backend_name() == "postgresql"
    assert parsed.database == "valeo_probe"
    engine = sa.create_engine(url, connect_args={"application_name": "agent:vvvo-mandantenfilter"})
    try:
        with engine.connect() as conn:
            outer = conn.begin()
            try:
                conn.exec_driver_sql("""CREATE TEMP TABLE vvvo_guard (
                    id text PRIMARY KEY, tenant_id text NOT NULL, betrieb_name text,
                    vvvo_nummer text, letzte_pruefung_am date, naechste_pruefung_am date
                ) ON COMMIT DROP""")
                conn.exec_driver_sql("""CREATE TEMP TABLE sachkunde_guard (
                    id text PRIMARY KEY, tenant_id text NOT NULL, mitarbeiter_name text,
                    zertifikat_art text, ablauf_datum date
                ) ON COMMIT DROP""")
                conn.exec_driver_sql("""INSERT INTO vvvo_guard VALUES
                    ('eigen', 'a', 'Pruefhof A', 'A', NULL, NULL),
                    ('fremd', 'b', 'Pruefhof B', 'B', NULL, NULL)""")
                conn.exec_driver_sql("""INSERT INTO sachkunde_guard VALUES
                    ('eigen', 'a', 'Test A', 'Test', '2099-01-01'),
                    ('fremd', 'b', 'Test B', 'Test', '2099-01-01')""")
                with Session(bind=conn, join_transaction_mode="create_savepoint") as session:
                    class TempAdapter:
                        """Nur Tabellenziele ersetzen; SQL und Bindewerte unveraendert auswerten."""
                        before_update = None

                        def execute(self, statement, params):
                            sql = str(statement)
                            sql = sql.replace("domain_compliance.compliance_vvvo_register", "pg_temp.vvvo_guard")
                            sql = sql.replace("domain_compliance.compliance_sachkunde_register", "pg_temp.sachkunde_guard")
                            if sql.lstrip().startswith("UPDATE") and self.before_update:
                                action, self.before_update = self.before_update, None
                                action()
                            return session.execute(sa.text(sql), params)

                        def commit(self):
                            session.commit()

                    yield TempAdapter(), session
                assert outer.is_active, "Service-Commit darf die aeussere Testtransaktion nicht beenden"
            finally:
                outer.rollback()
    finally:
        engine.dispose()


def test_eigene_pruefung_speichert_und_fremde_daten_bleiben_unveraendert(daten):
    db, session = daten
    result = berechne_naechste_vvvo_pruefung(db, "eigen", "a", "2026-01-15")
    assert result["tenant_id"] == "a"
    assert result["naechste_pruefung_am"] == "2027-01-15"
    rows = session.execute(sa.text("SELECT id, letzte_pruefung_am, naechste_pruefung_am FROM pg_temp.vvvo_guard ORDER BY id")).all()
    assert rows == [("eigen", date(2026, 1, 15), date(2027, 1, 15)), ("fremd", None, None)]


@pytest.mark.parametrize("operation", ["pruefung", "status"])
def test_fremde_und_fehlende_id_sind_nicht_unterscheidbar(daten, operation):
    db, session = daten
    errors = []
    for attempt in range(2):
        with pytest.raises(VVVOError) as error:
            if operation == "pruefung":
                berechne_naechste_vvvo_pruefung(db, "fremd", "a", "2026-01-15")
            else:
                get_sachkunde_status(db, "fremd", "a")
        errors.append(str(error.value))
        if attempt == 0:
            # Identische Anfrage: erst fremde Zeile vorhanden, dann dieselbe ID unbekannt.
            table = "vvvo_guard" if operation == "pruefung" else "sachkunde_guard"
            session.execute(sa.text(f"DELETE FROM pg_temp.{table} WHERE id = 'fremd'"))
    assert errors[0] == errors[1]
    assert "nicht gefunden" in errors[0]
    assert session.execute(sa.text("SELECT count(*) FROM pg_temp.vvvo_guard WHERE letzte_pruefung_am IS NOT NULL")).scalar() == 0
    own = get_sachkunde_status(db, "eigen", "a")
    assert own["tenant_id"] == "a"
    assert own["gueltig"] is True


def test_mandantenwechsel_zwischen_lesen_und_schreiben_meldet_keinen_erfolg(daten):
    db, session = daten
    db.before_update = lambda: session.execute(sa.text("UPDATE pg_temp.vvvo_guard SET tenant_id = 'b' WHERE id = 'eigen'"))
    with pytest.raises(VVVOError, match="nicht gefunden"):
        berechne_naechste_vvvo_pruefung(db, "eigen", "a", "2026-01-15")
    row = session.execute(sa.text("SELECT tenant_id, letzte_pruefung_am, naechste_pruefung_am FROM pg_temp.vvvo_guard WHERE id = 'eigen'")).one()
    assert row == ("b", None, None)
