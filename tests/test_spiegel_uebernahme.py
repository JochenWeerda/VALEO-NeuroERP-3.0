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
MAPPING.update({"QUELLE": "source_ref", "KUNDENNR": "kundennummer", "KUNDNAME": "name", "STRASSE": "strasse",
                "PLZ": "plz", "ORT": "ort", "STAAT": "land", "USTID": "ust_id", "DEBITORKTO": "debitorkonto",
                "SPERRE": "gesperrt", "LIEFERANTENNR": "lieferantennummer", "KREDITORKTO": "kreditorkonto", "LAGER": "lager", "BESTAND": "menge", "EINHEIT": "einheit"})
VERTRAG = {"encoding": "utf-8", "record_types": ["artikel", "kunde", "lieferant", "bestand"], "sample_hash": "synthetisch", "export_stand": "Test"}


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
                        "DELETE FROM domain_inventory.bestandsbuchung_schluessel WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.spiegel_quellreferenzen WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                        "DELETE FROM domain_crm.customers WHERE tenant_id = :t",
                        "DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = :t",
                        "DELETE FROM domain_crm.business_partners WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
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
        {"TYP": "rechnung", "ARTIKELNR": "K1"},
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


def test_nur_l3_spiegel_profil_wird_uebernommen(mandant):
    LegacyInterfaceAdapterService(SessionLocal(), mandant).configure(
        "l3_standard",
        {"format_contract": {**VERTRAG, "delimiter": ";"}, "field_mapping": MAPPING},
        actor="test", reason="M6-Profilguard")
    with SessionLocal() as db:
        dienst = LegacyInterfaceAdapterService(db, mandant)
        batch = dienst.intake("l3_standard", "abzug-fremd", {"records": [_artikel("151704", "x")]}, actor="test")["id"]
        dienst.stage(batch, actor="test", reason="M6")
        dienst.reconcile(batch, actor="test", reason="M6")
        dienst.approve(batch, actor="test", reason="M6")
    with SessionLocal() as db, pytest.raises(LegacyAdapterError, match="l3_spiegel"):
        uebernehme(db, mandant, batch, actor="test", reason="M6")


def test_soft_delete_wird_bei_gleichem_l3_inhalt_wiederbelebt(mandant):
    _lauf(mandant, "abzug-1", [_artikel("151704", "ZINTAN PLATIN")])
    with SessionLocal() as db:
        db.execute(text(
            "UPDATE domain_inventory.articles SET deleted_at = now(), is_active = false WHERE tenant_id = :t "
            "AND article_number = '151704'"), {"t": mandant})
        db.commit()

    ergebnis = _lauf(mandant, "abzug-2", [_artikel("151704", "ZINTAN PLATIN")])

    with SessionLocal() as db:
        zeile = db.execute(text(
            "SELECT name, is_active, deleted_at FROM domain_inventory.articles WHERE tenant_id = :t "
            "AND article_number = '151704'"), {"t": mandant}).mappings().one()
        bericht = differenzbericht(db, mandant, db.execute(text(
            "SELECT id FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t AND external_id = "
            "'abzug-2'"), {"t": mandant}).scalar_one())

    assert (ergebnis["geaendert"], ergebnis["unveraendert"], ergebnis["fehler"]) == (1, 0, 0)
    assert zeile["deleted_at"] is None and zeile["is_active"] is True
    assert "deleted_at" in bericht["geaendert"][0]["felder"]


def test_protokoll_ist_unveraenderlich(mandant):
    _lauf(mandant, "abzug-1", [_artikel("151704", "x")])
    with SessionLocal() as db, pytest.raises(Exception, match="unveraenderlich"):
        db.execute(text("UPDATE domain_integration.spiegel_protokoll SET ergebnis = 'neu' WHERE tenant_id = :t"),
                   {"t": mandant})


def _kunde(nr: str, name: str, **mehr) -> dict:
    return {"TYP": "kunde", "QUELLE": nr, "KUNDENNR": nr, "KUNDNAME": name, "STRASSE": "Hauptstr. 1", "PLZ": "26721",
            "ORT": "Emden", "STAAT": "D", "DEBITORKTO": nr, **mehr}


def _kundenzeilen(t: str) -> list[tuple]:
    with SessionLocal() as db:
        return [tuple(r) for r in db.execute(text(
            "SELECT customer_number, company_name, address->>'street', postal_code, city, is_active "
            "FROM domain_crm.customers WHERE tenant_id = :t ORDER BY customer_number"), {"t": t})]


def test_kunden_werden_angelegt_wiederholt_unveraendert_mit_l3_debitorenkonto(mandant):
    records = [_kunde("10001", "Hof Janssen"), _kunde("10002", "Hof Meyer", SPERRE="1")]

    erster = _lauf(mandant, "kd-1", records)
    zweiter = _lauf(mandant, "kd-2", records)
    with SessionLocal() as db:
        bericht = differenzbericht(db, mandant, db.execute(text(
            "SELECT id FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t AND external_id = 'kd-1'"),
            {"t": mandant}).scalar_one())

    assert (erster["neu"], zweiter["unveraendert"]) == (2, 2)
    assert _kundenzeilen(mandant) == [("10001", "Hof Janssen", "Hauptstr. 1", "26721", "Emden", True),
                                      ("10002", "Hof Meyer", "Hauptstr. 1", "26721", "Emden", False)]
    assert bericht["nicht_zugeordnet"] == {}
    with SessionLocal() as db:  # Nutzerentscheid 25.11.2026: L3-Debitorennummer = Konto am Geschaeftspartner
        konten = [tuple(r) for r in db.execute(text(
            "SELECT c.customer_number, bp.debtor_account FROM domain_crm.customers c JOIN domain_crm.business_partners "
            "bp ON bp.partner_id::text = c.business_partner_id::text WHERE c.tenant_id = :t ORDER BY 1"), {"t": mandant})]
    assert konten == [("10001", "10001"), ("10002", "10002")]


def test_vergebenes_debitorenkonto_wird_fehlerzeile(mandant):
    ergebnis = _lauf(mandant, "kd-1", [_kunde("10001", "Hof Janssen"), _kunde("10003", "Hof Ohne", DEBITORKTO="10001")])

    assert (ergebnis["neu"], ergebnis["fehler"]) == (1, 1)
    assert [z[0] for z in _kundenzeilen(mandant)] == ["10001"]


def test_kundenaenderung_und_fremdbestand(mandant):
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                        "VALUES (:id, :t, '10099', 'von Hand')"), {"id": str(uuid.uuid4()), "t": mandant})
        db.commit()
    _lauf(mandant, "kd-1", [_kunde("10001", "Hof Janssen")])
    zweiter = _lauf(mandant, "kd-2", [_kunde("10001", "Hof Janssen GbR"), _kunde("10099", "schon da")])

    assert (zweiter["geaendert"], zweiter["fehler"]) == (1, 1)
    assert [z[:2] for z in _kundenzeilen(mandant)] == [("10001", "Hof Janssen GbR"), ("10099", "von Hand")]


def _lager(t: str, code: str = "L1") -> None:
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                        "VALUES (:id, :t, :c, 'Hauptlager')"), {"id": str(uuid.uuid4()), "t": t, "c": code})
        db.commit()


def _bestand(nr: str, menge: str, lager: str = "L1") -> dict:
    return {"TYP": "bestand", "QUELLE": f"{nr}@{lager}", "ARTNR": nr, "LAGER": lager, "BESTAND": menge, "EINHEIT": "St"}


def _saldo(t: str, nr: str) -> tuple:
    with SessionLocal() as db:
        return tuple(db.execute(text(
            "SELECT COUNT(*), COALESCE(SUM(m.quantity), 0) FROM domain_inventory.inventory_stock_movements m "
            "JOIN domain_inventory.articles a ON a.id = m.article_id WHERE m.tenant_id = :t AND a.article_number = :n"),
            {"t": t, "n": nr}).one())


def test_anfangsbestand_einmal_gebucht_und_wiederholung_bucht_nicht(mandant):
    _lager(mandant)
    _lauf(mandant, "ab-1", [_artikel("151704", "x"), _bestand("151704", "12")])
    zweiter = _lauf(mandant, "ab-2", [_artikel("151704", "x"), _bestand("151704", "12")])

    assert zweiter["unveraendert"] == 2
    anzahl, menge = _saldo(mandant, "151704")
    assert (anzahl, float(menge)) == (1, 12.0)


def test_abweichung_in_valeo_wird_gemeldet_nicht_gebucht(mandant):
    from decimal import Decimal

    from app.domains.inventory.application.services.inventory_service import InventoryService

    _lager(mandant)
    _lauf(mandant, "ab-1", [_artikel("151704", "x"), _bestand("151704", "12")])
    with SessionLocal() as db:  # Abgang in VALEO, den L3 (noch) nicht kennt
        artikel, lager = db.execute(text(
            "SELECT a.id, w.id FROM domain_inventory.articles a, domain_inventory.warehouses w "
            "WHERE a.tenant_id = :t AND w.tenant_id = :t"), {"t": mandant}).one()
        InventoryService(db).process_stock_movement(str(artikel), str(lager), "out", Decimal("2"), unit="St",
                                                    tenant_id=mandant, buchungsschluessel="test:abgang")
    zweiter = _lauf(mandant, "ab-2", [_artikel("151704", "x"), _bestand("151704", "12")])

    with SessionLocal() as db:
        bericht = differenzbericht(db, mandant, db.execute(text(
            "SELECT id FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t AND external_id = 'ab-2'"),
            {"t": mandant}).scalar_one())
    assert zweiter["geaendert"] == 1
    assert bericht["geaendert"][0]["felder"] == {"menge": {"valeo": "10", "l3": "12"}}
    assert _saldo(mandant, "151704")[0] == 2  # keine Korrekturbuchung


def test_bestand_ohne_artikel_lager_oder_mit_fremdbestand_wird_fehlerzeile(mandant):
    from decimal import Decimal

    from app.domains.inventory.application.services.inventory_service import InventoryService

    _lager(mandant)
    _lauf(mandant, "ab-0", [_artikel("151704", "x"), _artikel("151705", "y")])
    with SessionLocal() as db:
        artikel, lager = db.execute(text(
            "SELECT a.id, w.id FROM domain_inventory.articles a, domain_inventory.warehouses w "
            "WHERE a.tenant_id = :t AND w.tenant_id = :t AND a.article_number = '151705'"), {"t": mandant}).one()
        InventoryService(db).process_stock_movement(str(artikel), str(lager), "in", Decimal("5"), unit="St",
                                                    tenant_id=mandant, buchungsschluessel="test:zugang")

    ergebnis = _lauf(mandant, "ab-1", [_bestand("999999", "1"), _bestand("151704", "1", lager="L9"),
                                        _bestand("151705", "7")])

    assert (ergebnis["neu"], ergebnis["fehler"]) == (0, 3)


def _lieferant(nr: str, name: str, **mehr) -> dict:
    return {"TYP": "lieferant", "QUELLE": f"L{nr}", "LIEFERANTENNR": nr, "KUNDNAME": name, "PLZ": "26000",
            "STAAT": "D", "KREDITORKTO": f"7{nr}", **mehr}


def _partnerkonten(t: str) -> list[tuple]:
    with SessionLocal() as db:
        return [tuple(r) for r in db.execute(text(
            "SELECT name_1, debtor_account, creditor_account FROM domain_crm.business_partners WHERE tenant_id = :t "
            "ORDER BY name_1"), {"t": t})]


def test_lieferant_mit_l3_kreditorenkonto_und_wiederholung(mandant):
    erster = _lauf(mandant, "lf-1", [_lieferant("0001", "Saatzucht Nord")])
    zweiter = _lauf(mandant, "lf-2", [_lieferant("0001", "Saatzucht Nord")])

    assert (erster["neu"], zweiter["unveraendert"]) == (1, 1)
    assert _partnerkonten(mandant) == [("Saatzucht Nord", None, "70001")]


def test_landwirt_als_kunde_und_lieferant_ist_ein_partner_mit_zwei_konten(mandant):
    _lauf(mandant, "lf-1", [_kunde("10001", "Hof Janssen", USTID="DE123456789"),
                            _lieferant("0002", "Hof Janssen", USTID="DE123456789")])

    assert _partnerkonten(mandant) == [("Hof Janssen", "10001", "70002")]


def test_vergebenes_kreditorenkonto_wird_fehlerzeile(mandant):
    ergebnis = _lauf(mandant, "lf-1", [_lieferant("0001", "Saatzucht Nord"),
                                       _lieferant("0003", "Agrarhandel Sued", KREDITORKTO="70001")])

    assert (ergebnis["neu"], ergebnis["fehler"]) == (1, 1)

