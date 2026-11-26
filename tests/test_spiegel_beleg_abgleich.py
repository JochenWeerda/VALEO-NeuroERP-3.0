"""Spiegelbetrieb: taeglicher Belegabgleich L3 gegen VALEO (M6, 26.11.2026) - gegen die echte DB; liest nur."""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.legacy_interface_adapter_service import LegacyInterfaceAdapterService
from app.services.spiegel_beleg_abgleich import abgleichen

pytestmark = pytest.mark.integration

MAPPING = {"TYP": "record_type", "QUELLE": "source_ref", "BELEGART": "belegart", "BELEGNR": "belegnummer",
           "DATUM": "datum", "NETTO": "netto", "BRUTTO": "brutto"}
VERTRAG = {"encoding": "utf-8", "record_types": ["beleg"], "sample_hash": "synthetisch", "export_stand": "Test"}


@pytest.fixture
def mandant():
    t = f"bg-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        for art, nr, datum, netto, brutto, quelle in (
                ("sales_invoice", "VR-1", "2026-11-20", "100.00", "119.00", "l3"),
                ("sales_invoice", "VR-2", "2026-11-20", "50.00", "59.50", "l3"),
                ("sales_delivery", "VL-9", "2026-11-21", "0", "0", "l3"),            # nur in VALEO
                ("sales_invoice", "VR-7", "2026-11-20", "10.00", "11.90", "docflow.ui")):  # nicht aus dem Spiegel
            db.execute(text("INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, "
                            "document_date, total_net, total_gross, source_system, source_ref) "
                            "VALUES (:id, :t, :art, :nr, :d, :n, :b, :q, :nr)"),
                       {"id": str(uuid.uuid4()), "t": t, "art": art, "nr": nr, "d": datum, "n": netto, "b": brutto,
                        "q": quelle})
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
                        "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _beleg(art: str, nr: str, datum: str, netto: str, brutto: str) -> dict:
    return {"TYP": "beleg", "QUELLE": f"{art}:{nr}", "BELEGART": art, "BELEGNR": nr, "DATUM": datum, "NETTO": netto,
            "BRUTTO": brutto}


def _batch(t: str, records: list[dict]) -> str:
    with SessionLocal() as db:
        dienst = LegacyInterfaceAdapterService(db, t)
        batch = dienst.intake("l3_spiegel", f"bg-{uuid.uuid4().hex[:4]}", {"records": records}, actor="test")["id"]
        for schritt in (dienst.stage, dienst.reconcile, dienst.approve):
            schritt(batch, actor="test", reason="M6")
        return batch


def test_belegabgleich_findet_gleich_abweichend_fehlend_und_fehlt_in_l3(mandant):
    batch = _batch(mandant, [_beleg("sales_invoice", "VR-1", "20.11.2026", "100,00", "119,00"),
                             _beleg("sales_invoice", "VR-2", "20.11.2026", "50.00", "60.00"),
                             _beleg("sales_invoice", "VR-3", "21.11.2026", "5.00", "5.95"),
                             _beleg("rechnung_alt", "X-1", "21.11.2026", "1", "1")])
    with SessionLocal() as db:
        vorher = db.execute(text("SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t"),
                            {"t": mandant}).scalar_one()
        ergebnis = abgleichen(db, mandant, batch, actor="test", reason="M6")
        nachher = db.execute(text("SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t"),
                             {"t": mandant}).scalar_one()

    assert (ergebnis["unveraendert"], ergebnis["geaendert"], ergebnis["fehler"]) == (1, 1, 2)
    assert ergebnis["fehlt_in_l3"] == [{"belegart": "sales_delivery", "belegnummer": "VL-9"}]  # VR-7 ist nicht 'l3'
    assert ergebnis["summen"]["sales_invoice"] == {"l3": "184.95", "valeo": "178.50"}
    assert ergebnis["zeitraum"] == ["2026-11-20", "2026-11-21"]
    assert ergebnis["abweichungsfrei"] is False
    assert vorher == nachher  # liest nur


def test_abweichungsfreier_tagesabgleich(mandant):
    batch = _batch(mandant, [_beleg("sales_invoice", "VR-1", "2026-11-20", "100.00", "119.00"),
                             _beleg("sales_invoice", "VR-2", "2026-11-20", "50.00", "59.50")])
    with SessionLocal() as db:
        ergebnis = abgleichen(db, mandant, batch, actor="test", reason="M6")

    assert ergebnis["unveraendert"] == 2
    assert ergebnis["abweichungsfrei"] is True
