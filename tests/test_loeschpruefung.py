"""Loeschpruefung nach Aufbewahrungsfristen (M7, 26.11.2026) - gegen die echte DB; der Bericht loescht nie."""
from __future__ import annotations

import uuid
from datetime import date

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.loeschpruefung import pruefe

pytestmark = pytest.mark.integration

STICHTAG = date(2035, 6, 1)


@pytest.fixture
def mandant():
    t = f"lp-{uuid.uuid4().hex[:6]}"
    ids = {}
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        for schluessel, art, datum in (("er_alt", "purchase_invoice", "2026-03-01"), ("ar_neu", "sales_invoice", "2028-01-10"),
                                       ("auftrag", "sales_order", "2026-05-01"), ("auftrag_gesperrt", "sales_order", "2026-05-02"),
                                       ("ls_mit_rechnung", "sales_delivery", "2027-12-20"),
                                       ("we_ohne_rechnung", "goods_receipt", "2026-03-01"), ("test", "TEST", "2020-01-01")):
            ids[schluessel] = str(uuid.uuid4())
            db.execute(text("INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, document_date) "
                            "VALUES (:id, :t, :art, :nr, :d)"), {"id": ids[schluessel], "t": t, "art": art, "nr": schluessel,
                                                                 "d": datum})
        db.execute(text("INSERT INTO domain_docflow.document_header_links (id, tenant_id, from_header_id, to_header_id, "
                        "relation_type) VALUES (:id, :t, :von, :nach, 'invoiced_by')"),
                   {"id": str(uuid.uuid4()), "t": t, "von": ids["ls_mit_rechnung"], "nach": ids["ar_neu"]})
        db.execute(text("INSERT INTO public.gobd_loeschsperren (id, tenant_id, dokument_id, dokument_typ, sperrgrund, "
                        "hold_start_date, status) VALUES (:id, :t, :d, 'sales_order', 'Aussenpruefung', '2030-01-01', 'ACTIVE')"),
                   {"id": str(uuid.uuid4()), "t": t, "d": ids["auftrag_gesperrt"]})
        ids["journal"] = str(uuid.uuid4())
        db.execute(text("INSERT INTO domain_erp.journal_entries (id, tenant_id, entry_number, entry_date, posting_date, status) "
                        "VALUES (:id, :t, 'JE-1', '2026-03-01', '2026-03-01', 'draft')"), {"id": ids["journal"], "t": t})
        db.commit()
    try:
        yield t, ids
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                        "DELETE FROM public.gobd_loeschsperren WHERE tenant_id = :t",
                        "DELETE FROM domain_docflow.document_header_links WHERE tenant_id = :t",
                        "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _kat(bericht: dict, typ: str) -> dict:
    return next(k for k in bericht["kategorien"] if k["dokumenttyp"] == typ)


def test_bericht_ordnet_jede_kategorie_der_geltenden_frist_zu(mandant):
    t, ids = mandant
    with SessionLocal() as db:
        vorher = db.execute(text("SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t"),
                            {"t": t}).scalar_one()
        bericht = pruefe(db, t, heute=STICHTAG)
        nachher = db.execute(text("SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t"),
                             {"t": t}).scalar_one()

    er, ar = _kat(bericht, "ap_invoice"), _kat(bericht, "ar_invoice")
    assert (er["loeschbar"], er["loeschbar_ids"]) == (1, [ids["er_alt"]])        # 2026 + 8 Jahre -> 31.12.2034
    assert (ar["in_frist"], ar["loeschbar"]) == (1, 0)                            # 2028 + 8 -> 31.12.2036
    auftrag = _kat(bericht, "handelsbrief")
    assert (auftrag["loeschbar"], auftrag["gesperrt"]) == (1, 1)                  # 6 Jahre; einer unter Loeschsperre
    ls = _kat(bericht, "lieferschein")
    assert (ls["gesamt"], ls["loeschbar"], ls["vorsichtig_als_beleg"]) == (2, 2, 1)  # mit Rechnung: Rechnungsdatum
    assert _kat(bericht, "journal_entry")["in_frist"] == 1                        # Buecher 10 Jahre -> 31.12.2036
    assert "TEST" not in {k["dokumenttyp"] for k in bericht["kategorien"]}
    assert bericht["vorbehalt"] and vorher == nachher                             # Vorbehalt; nichts geloescht


def test_offene_festsetzungsfrist_hemmt_jede_loeschung(mandant):
    t, _ = mandant
    with SessionLocal() as db:
        bericht = pruefe(db, t, heute=STICHTAG, festsetzungsfrist_offen_bis=date(2036, 12, 31))

    assert sum(k["loeschbar"] for k in bericht["kategorien"]) == 0
    assert bericht["vorbehalt"] is None
