"""L3-Testdatenabzug: Klartextsperre und wertfreie Ausgabe (DSGVO, 25.11.2026) - ohne Datenbank."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_PFAD = Path(__file__).resolve().parents[1] / "scripts" / "l3_testdaten_import.py"
_spec = importlib.util.spec_from_file_location("l3_testdaten_import", _PFAD)
skript = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(skript)


@pytest.mark.parametrize(("zeile", "art"), [
    ({"KUNDNAME": "Hof Janssen, j.janssen@example.org"}, "E-Mail"),
    ({"BEMERKUNG": "Tel 04921 123456"}, "Telefon"),
    ({"BANK": "DE89 3704 0044 0532 0130 00"}, "IBAN"),
    ({"ANSCHRIFT": "Hauptstrasse 12"}, "Strasse"),
])
def test_klartext_wird_erkannt(zeile, art):
    assert skript.klartext_funde([zeile])[art] == 1


def test_pseudonymisierte_zeile_ist_frei():
    zeile = {"TYP": "kunde", "QUELLE": "10001", "KUNDENNR": "10001", "KUNDNAME": "Testkunde 10001", "PLZ": "26000",
             "DEBITORKTO": "10001", "BEZEICHN1": "ZINTAN PLATIN PACK 10 L + 8,4 L"}
    assert not skript.klartext_funde([zeile])


def test_fehlerart_enthaelt_keine_werte():
    art = skript.fehlerart("Artikel 151704 existiert bereits ohne L3-Quellreferenz - Zuordnung klaeren")
    assert art.startswith("Artikel # existiert bereits") and not any(z.isdigit() for z in art)
    assert "Hof" not in skript.fehlerart("Betrag 'Hof Janssen' ist keine Zahl")


def test_csv_mit_semikolon_und_bom(tmp_path):
    datei = tmp_path / "l3_abzug_artikel_20261125.csv"
    datei.write_text("﻿TYP;QUELLE;ARTNR;BEZEICHN1\nartikel;151704;151704;ZINTAN\n", encoding="utf-8")
    assert skript.lies(datei) == [{"TYP": "artikel", "QUELLE": "151704", "ARTNR": "151704", "BEZEICHN1": "ZINTAN"}]


def test_einlesen_bricht_bei_klartext_ab_bevor_die_datenbank_beruehrt_wird(tmp_path, capsys):
    (tmp_path / "l3_abzug_kunde_20261125.csv").write_text(
        "TYP;QUELLE;KUNDENNR;KUNDNAME\nkunde;10001;10001;Hof Janssen j@example.org\n", encoding="utf-8")
    assert skript.einlesen(tmp_path, "l3-test") == 2
    ausgabe = capsys.readouterr().out
    assert "ABBRUCH" in ausgabe and "example.org" not in ausgabe and "Janssen" not in ausgabe


def test_loeschen_nur_fuer_testmandanten():
    assert skript.loeschen("00000000-0000-0000-0000-000000000001") == 2


@pytest.mark.integration
def test_durchlauf_einlesen_und_loeschen(tmp_path, capsys):
    import uuid

    from sqlalchemy import text

    from app.core.database import SessionLocal

    mandant = f"l3-test-{uuid.uuid4().hex[:6]}"
    (tmp_path / "l3_abzug_kunde_20261125.csv").write_text(
        "TYP;QUELLE;KUNDENNR;KUNDNAME;PLZ;STAAT;DEBITORKTO\n"
        "kunde;10001;10001;Testkunde 10001;26000;D;10001\n"
        "kunde;10002;10002;Testkunde 10002;26000;D;10002\n", encoding="utf-8")
    try:
        assert skript.einlesen(tmp_path, mandant) == 0
        ausgabe = capsys.readouterr().out
        assert "kunde" in ausgabe and "neu 2" in ausgabe and "Testkunde" not in ausgabe
        with SessionLocal() as db:
            assert db.execute(text("SELECT count(*) FROM domain_crm.customers WHERE tenant_id = :t"),
                              {"t": mandant}).scalar_one() == 2
    finally:
        assert skript.loeschen(mandant) == 0
    with SessionLocal() as db:
        assert db.execute(text("SELECT count(*) FROM domain_crm.customers WHERE tenant_id = :t"),
                          {"t": mandant}).scalar_one() == 0
        assert db.execute(text("SELECT count(*) FROM domain_shared.tenants WHERE id = :t"),
                          {"t": mandant}).scalar_one() == 0
