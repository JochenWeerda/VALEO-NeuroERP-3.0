"""Spiegelbetrieb L3 -> VALEO: Uebernahme freigegebener Batches (M6, 25.11.2026) - gegen die echte DB.

Ganze Strecke ueber die vorhandene Adapterstrecke: Profil, Annahme, Staging, Abgleich, Freigabe, Uebernahme.
"""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.legacy_interface_adapter_service import LegacyAdapterError, LegacyInterfaceAdapterService
from app.services.spiegel_uebernahme import differenzbericht, uebernehme

pytestmark = pytest.mark.integration

MAPPING = {"TYP": "record_type", "ARTIKELNR": "source_ref", "ARTNR": "artikelnummer", "BEZEICHN1": "bezeichnung",
           "BEZEICHN2": "bezeichnung2", "ARTIKELGRP": "artikelgruppe", "ME1": "mengeneinheit_nr",
           "GESPERRT": "gesperrt"}
VERTRAG = {"encoding": "utf-8", "record_types": ["artikel"], "sample_hash": "synthetisch", "export_stand": "Test"}


def _artikel(nr: str, bezeichnung: str, **mehr) -> dict:
    return {"TYP": "artikel", "ARTIKELNR": nr, "ARTNR": nr, "BEZEICHN1": bezeichnung, "ARTIKELGRP": "151",
            "ME1": "2", **mehr}


@pytest.fixture
def mandant():
    t = f"sp-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.commit()
    _warengruppe(t, "151")
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.artikel_mengeneinheiten (id, tenant_id, einheit_kuerzel, "
                        "bezeichnung, nummer) VALUES (:id, :t, 'St', 'Stueck', 2)"), {"id": str(uuid.uuid4()), "t": t})
        db.commit()
    LegacyInterfaceAdapterService(SessionLocal(), t).configure(
        "l3_spiegel", {"format_contract": VERTRAG, "field_mapping": MAPPING}, actor="test", reason="M6-Test")
    try:
        yield t
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_integration.spiegel_protokoll WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.spiegel_quellreferenzen WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_staging WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_audit WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_profiles WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.artikel_mengeneinheiten WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.warengruppen WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.oberwarengruppen WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.hauptwarengruppen WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _warengruppe(t: str, nr: str) -> None:
    haupt, ober = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.hauptwarengruppen (id, tenant_id, gruppe_nr, bezeichnung) "
                        "VALUES (:id, :t, '1', 'Handelsware')"), {"id": haupt, "t": t})
        db.execute(text("INSERT INTO domain_shared.oberwarengruppen (id, tenant_id, gruppe_nr, bezeichnung, haupt_id) "
                        "VALUES (:id, :t, '15', 'Pflanzenschutz', :h)"), {"id": ober, "t": t, "h": haupt})
        db.execute(text("INSERT INTO domain_shared.warengruppen (id, tenant_id, gruppe_nr, bezeichnung, ober_id, "
                        "aktiv) VALUES (:id, :t, :nr, 'Pflanzenschutz Grosspackung', :o, true)"),
                   {"id": str(uuid.uuid4()), "t": t, "nr": nr, "o": ober})
        db.commit()


def _lauf(t: str, abzug: str, records: list[dict]) -> dict:
    with SessionLocal() as db:
        dienst = LegacyInterfaceAdapterService(db, t)
        batch = dienst.intake("l3_spiegel", abzug, {"records": records}, actor="test")["id"]
        dienst.stage(batch, actor="test", reason="M6")
        dienst.reconcile(batch, actor="test", reason="M6")
        dienst.approve(batch, actor="test", reason="M6")
    with SessionLocal() as db:
        return uebernehme(db, t, batch, actor="test", reason="M6")


def _artikelzeilen(t: str) -> list[tuple]:
    with SessionLocal() as db:
        return [tuple(r) for r in db.execute(text(
            "SELECT article_number, name, warengruppe, unit, is_active FROM domain_inventory.articles "
            "WHERE tenant_id = :t ORDER BY article_number"), {"t": t})]


def test_erster_lauf_legt_an_und_wiederholung_aendert_nichts(mandant):
    records = [_artikel("151704", "ZINTAN PLATIN PACK 10 L + 8,4 L"), _artikel("151705", "Testmittel", GESPERRT="J")]

    erster = _lauf(mandant, "abzug-1", records)
    zweiter = _lauf(mandant, "abzug-2", records)  # neuer Abzug, gleicher Inhalt

    assert (erster["neu"], erster["fehler"]) == (2, 0)
    assert (zweiter["neu"], zweiter["unveraendert"], zweiter["geaendert"]) == (0, 2, 0)
    assert _artikelzeilen(mandant) == [("151704", "ZINTAN PLATIN PACK 10 L + 8,4 L", "151", "St", True),
                                       ("151705", "Testmittel", "151", "St", False)]


def test_geaenderter_inhalt_aktualisiert_und_protokolliert_die_felder(mandant):
    _lauf(mandant, "abzug-1", [_artikel("151704", "ZINTAN PLA alt")])
    _lauf(mandant, "abzug-2", [_artikel("151704", "ZINTAN PLA neu")])

    with SessionLocal() as db:
        bericht = differenzbericht(db, mandant, db.execute(text(
            "SELECT id FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t AND external_id = "
            "'abzug-2'"), {"t": mandant}).scalar_one())
        version = db.execute(text("SELECT version FROM domain_integration.spiegel_quellreferenzen "
                                  "WHERE tenant_id = :t"), {"t": mandant}).scalar_one()

    assert bericht["summen"]["geaendert"] == 1 and version == 2
    assert bericht["geaendert"][0]["felder"] == {"name": {"valeo": "ZINTAN PLA alt", "l3": "ZINTAN PLA neu"}}
    assert _artikelzeilen(mandant)[0][1] == "ZINTAN PLA neu"


def test_unbekannte_bezuege_und_fremdbestand_werden_fehlerzeilen_ohne_abbruch(mandant):
    with SessionLocal() as db:  # in VALEO von Hand angelegt, ohne L3-Quellreferenz
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name) "
                        "VALUES (:id, :t, '151799', 'von Hand')"), {"id": str(uuid.uuid4()), "t": mandant})
        db.commit()

    ergebnis = _lauf(mandant, "abzug-1", [
        _artikel("151704", "gut"),
        _artikel("999001", "Gruppe fehlt", ARTIKELGRP="999"),
        _artikel("151706", "Einheit fehlt", ME1="77"),
        _artikel("151799", "schon da"),
        {"TYP": "kunde", "ARTIKELNR": "K1"},
    ])

    with SessionLocal() as db:
        bericht = differenzbericht(db, mandant, db.execute(text(
            "SELECT id FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t"),
            {"t": mandant}).scalar_one())
    gruende = sorted(f["fehler"].split(" ")[0] + ":" + str(f["quellschluessel"]) for f in bericht["fehler"])

    assert (ergebnis["neu"], ergebnis["fehler"]) == (1, 4)
    assert gruende == ["Artikel:151799", "Artikelgruppe:999001", "Mengeneinheit:151706", "Objektart:K1"]
    assert [z[0] for z in _artikelzeilen(mandant)] == ["151704", "151799"]  # Handbestand unberuehrt


def test_nur_freigegebene_batches_werden_uebernommen(mandant):
    with SessionLocal() as db:
        dienst = LegacyInterfaceAdapterService(db, mandant)
        batch = dienst.intake("l3_spiegel", "abzug-x", {"records": [_artikel("151704", "x")]}, actor="test")["id"]
        dienst.stage(batch, actor="test", reason="M6")
    with SessionLocal() as db, pytest.raises(LegacyAdapterError, match="freigegebene"):
        uebernehme(db, mandant, batch, actor="test", reason="M6")
