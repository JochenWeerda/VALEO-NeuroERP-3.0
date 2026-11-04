"""Ruestlisten: die Tabelle existiert, der Weg arbeitet je Mandant (Migration ruestlisten_tabelle_20261103).

Vorher legte keine Migration ``domain_inventory.ruestlisten`` an: die Liste antwortete leer (Fehler verschluckt),
Anlegen und Statuswechsel mit 503, und ein Statuswechsel haette selbst mit Tabelle an seinem Antwortmodell mit
500 geendet. Geprueft wird als ``valeo_app`` mit RLS auf dem frischen Pruefstand (Transaktion, zurueckgerollt).
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints import ruestliste as weg
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, as_app, probe

pytestmark = pytest.mark.integration
TABELLE = "domain_inventory.ruestlisten"


@pytest.fixture()
def db():
    with probe((TABELLE,)) as conn:
        as_app(conn)
        sitzung = Session(bind=conn, join_transaction_mode="create_savepoint")
        try:
            yield sitzung
        finally:
            sitzung.close()


def _anlegen(db, auftrag: str, prioritaet: str = "NORMAL"):
    return weg.create_ruestliste(weg.RuestlisteCreate(
        auftrag_nr=auftrag, erstellt_fuer="lager-nord", prioritaet=prioritaet,
        positionen=[weg.RuestlistePosition(artikel_nr="4711", menge=40, lagerplatz="A-01")]), db)


def test_anlegen_auflisten_und_ablauf(db):
    with tenant_scope(A, "test"):
        neu = _anlegen(db, "AU-1", "EILIG")
        assert neu.status == "OFFEN"
        liste = weg.list_ruestlisten(status=None, db=db)
        assert [(r.auftrag_nr, r.prioritaet, r.positionen[0]["menge"]) for r in liste] == [("AU-1", "EILIG", 40)]
        assert liste[0].erstellt_am  # timestamptz kommt als ISO-Text an
        assert weg.bearbeiten(neu.ruestlisten_nr, db) == {"ruestlisten_nr": neu.ruestlisten_nr, "status": "IN_BEARBEITUNG"}
        assert weg.verarbeitet(neu.ruestlisten_nr, db)["status"] == "VERARBEITET"
        weg.bemerkung_hinzufuegen(neu.ruestlisten_nr, weg.RuestlisteBearbeiten(bemerkung="Palette 2 nachgereicht"), db)
        zeile = weg.list_ruestlisten(status="VERARBEITET", db=db)[0]
        assert zeile.verarbeitet_am
        with pytest.raises(HTTPException) as fehler:
            weg.abbrechen(neu.ruestlisten_nr, db)
        assert fehler.value.status_code == 409


def test_jeder_mandant_sieht_nur_seine_ruestlisten(db):
    with tenant_scope(A, "test"):
        nr_a = _anlegen(db, "AU-A").ruestlisten_nr
    with tenant_scope(B, "test"):
        _anlegen(db, "AU-B")
        assert [r.auftrag_nr for r in weg.list_ruestlisten(status=None, db=db)] == ["AU-B"]
        with pytest.raises(HTTPException) as fehler:
            weg.bearbeiten(nr_a, db)  # fremde Nummer: fuer B nicht vorhanden
        assert fehler.value.status_code == 404
    mandanten = db.execute(sa.text(f"SELECT count(DISTINCT tenant_id) FROM {TABELLE}")).scalar()  # nosec B608
    assert mandanten == 0  # ohne Mandantenkontext sieht valeo_app nichts


def test_pruefbedingungen_der_tabelle(db):
    with tenant_scope(A, "test"), pytest.raises(Exception):
        with db.begin_nested():
            db.execute(sa.text(f"INSERT INTO {TABELLE} (id, ruestlisten_nr, auftrag_nr, status, erstellt_fuer) "  # nosec B608
                               "VALUES ('x', 'RL-1', 'AU', 'UNBEKANNT', 'lager')"))


def test_fehler_wird_nicht_mehr_als_leere_liste_verschluckt():
    class Kaputt:
        def execute(self, *_a, **_k):
            raise RuntimeError("relation does not exist")

    with pytest.raises(HTTPException) as fehler:
        weg.list_ruestlisten(status=None, db=Kaputt())
    assert fehler.value.status_code == 503 and "relation" not in str(fehler.value.detail)
