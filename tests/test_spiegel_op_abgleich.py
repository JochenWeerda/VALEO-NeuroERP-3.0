"""Spiegelbetrieb: OP-Abgleich L3 gegen VALEO (M6, 25.11.2026) - gegen die echte DB; liest nur, bucht nie."""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.legacy_interface_adapter_service import LegacyAdapterError, LegacyInterfaceAdapterService
from app.services.spiegel_op_abgleich import abgleichen

pytestmark = pytest.mark.integration

MAPPING = {"TYP": "record_type", "QUELLE": "source_ref", "KONTONR": "konto", "RECHNNR": "rechnungsnr",
           "OFFENBETRAG": "offener_betrag"}
VERTRAG = {"encoding": "utf-8", "record_types": ["offener_posten"], "sample_hash": "synthetisch", "export_stand": "Test"}


@pytest.fixture
def mandant():
    t = f"op-{uuid.uuid4().hex[:6]}"
    partner = str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, "
                        "is_customer, debtor_account) VALUES (:p, :t, 'P1', 'Hof Janssen', true, '10001')"),
                   {"p": partner, "t": t})
        for nr, offen, status in (("R-1", "100.00", "offen"), ("R-2", "50.00", "teilweise"), ("R-4", "20.00", "offen"),
                                  ("R-5", "99.00", "storniert")):
            db.execute(text("INSERT INTO domain_erp.offene_posten (id, tenant_id, rechnungsnr, konto_typ, betrag, offen, "
                            "op_status, partner_id) VALUES (:id, :t, :nr, 'debitoren', :o, :o, :s, :p)"),
                       {"id": str(uuid.uuid4()), "t": t, "nr": nr, "o": offen, "s": status, "p": partner})
        db.commit()
    LegacyInterfaceAdapterService(SessionLocal(), t).configure(
        "l3_spiegel", {"format_contract": VERTRAG, "field_mapping": MAPPING}, actor="test", reason="M6-Test")
    try:
        yield t
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_integration.spiegel_protokoll WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_staging WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_audit WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_batches WHERE tenant_id = :t",
                        "DELETE FROM domain_integration.legacy_adapter_profiles WHERE tenant_id = :t",
                        "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                        "DELETE FROM domain_crm.business_partners WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _op(konto: str, nr: str, offen: str) -> dict:
    return {"TYP": "offener_posten", "QUELLE": f"{konto}/{nr}", "KONTONR": konto, "RECHNNR": nr, "OFFENBETRAG": offen}


def _batch(t: str, abzug: str, records: list[dict], *, freigeben: bool = True) -> str:
    with SessionLocal() as db:
        dienst = LegacyInterfaceAdapterService(db, t)
        batch = dienst.intake("l3_spiegel", abzug, {"records": records}, actor="test")["id"]
        dienst.stage(batch, actor="test", reason="M6")
        if freigeben:
            dienst.reconcile(batch, actor="test", reason="M6")
            dienst.approve(batch, actor="test", reason="M6")
        return batch


def test_op_abgleich_erkennt_gleich_abweichend_fehlend_und_unbekannt(mandant):
    batch = _batch(mandant, "op-1", [_op("10001", "R-1", "100,00"), _op("10001", "R-2", "60.00"),
                                     _op("10001", "R-3", "10.00"), _op("19999", "R-9", "5.00")])
    with SessionLocal() as db:
        vorher = db.execute(text("SELECT count(*), sum(offen) FROM domain_erp.offene_posten WHERE tenant_id = :t"),
                            {"t": mandant}).one()
        ergebnis = abgleichen(db, mandant, batch, actor="test", reason="M6")
        nachher = db.execute(text("SELECT count(*), sum(offen) FROM domain_erp.offene_posten WHERE tenant_id = :t"),
                             {"t": mandant}).one()

    assert (ergebnis["unveraendert"], ergebnis["geaendert"], ergebnis["fehler"]) == (1, 1, 2)
    assert ergebnis["fehlt_in_l3"] == [{"konto": "10001", "rechnungsnr": "R-4", "valeo_offen": "20.00"}]
    assert ergebnis["salden"]["10001"] == {"konto_typ": "debitoren", "l3": "170.00", "valeo": "170.00",
                                           "differenz": "0.00"}
    assert ergebnis["abweichungsfrei"] is False
    assert tuple(vorher) == tuple(nachher)  # liest nur


def test_abweichungsfreier_abgleich(mandant):
    batch = _batch(mandant, "op-2", [_op("10001", "R-1", "100.00"), _op("10001", "R-2", "50.00"),
                                     _op("10001", "R-4", "20.00")])
    with SessionLocal() as db:
        ergebnis = abgleichen(db, mandant, batch, actor="test", reason="M6")

    assert (ergebnis["unveraendert"], ergebnis["abweichungsfrei"]) == (3, True)


def test_nur_freigegebene_batches(mandant):
    batch = _batch(mandant, "op-3", [_op("10001", "R-1", "100.00")], freigeben=False)
    with SessionLocal() as db, pytest.raises(LegacyAdapterError, match="freigegebene"):
        abgleichen(db, mandant, batch, actor="test", reason="M6")
