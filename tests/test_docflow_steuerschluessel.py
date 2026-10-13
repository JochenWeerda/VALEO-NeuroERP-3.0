"""DocFlow-Rechnung: die Position nennt ihren Steuerschluessel, Finance bucht je Schluessel.

DocFlow fuehrt die Verkaufsbelege; die Rechnungsmaske der Navigation (``sales/invoice-editor``) schreibt
hierher. Bis zum 13.10.2026 trug die Position nur ``tax_rate`` (Vorgabe 0), und die Rechnung wurde mit den
Kopfsummen fest auf 8400 und 1776 gebucht, gleich welcher Satz in den Positionen stand.

Architekturentscheidung vom 13.10.2026: Der Verkauf fuehrt den Beleg, Finance ist die Buchungsautoritaet.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import docflow
from app.core.database import SessionLocal
from app.core.tenant import get_tenant_id
from app.finance.steuerschluessel import richte_skr03_ein
from app.services import docflow_service
from testgrenze import ersetze_nutzer


@pytest.fixture
def haus(monkeypatch):
    lauf = uuid.uuid4().hex[:6]
    mandant = f"df-{lauf}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        richte_skr03_ein(db, mandant)
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, is_active) "
            "VALUES (:id, :t, '1400', 'Forderungen aus Lieferungen und Leistungen', 'asset', true)"),
            {"id": f"{mandant}-1400", "t": mandant})
        db.commit()
    monkeypatch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    app = FastAPI()
    # Isolated tax business contract; production token verification is tested separately.
    app.dependency_overrides[get_tenant_id] = lambda: mandant
    app.include_router(docflow.router, prefix="/docflow")
    # Schreibende DocFlow-Wege verlangen seit dem 13.10.2026 die Anmeldung (Akteur der Statushistorie).
    ersetze_nutzer(app, "admin")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"lauf": lauf, "mandant": mandant, "client": client}
    finally:
        with SessionLocal() as db:
            # Statushistorie und Kommandoprotokoll sind unveraenderlich; Aufraeumen nur mit Wartungsschalter.
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            for sql in (
                "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
                "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
                "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
                "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_links WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_header_links WHERE tenant_id = :t",
                "DELETE FROM domain_docflow.document_postings WHERE header_id IN (SELECT id FROM domain_docflow.document_headers WHERE tenant_id = :t)",
                "DELETE FROM domain_docflow.document_items WHERE header_id IN (SELECT id FROM domain_docflow.document_headers WHERE tenant_id = :t)",
                "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
                "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                try:
                    with db.begin_nested():
                        db.execute(text(sql), {"t": mandant})
                except Exception:  # noqa: BLE001 — Nebentabellen des Belegprozesses, je nach Lauf leer oder ohne Mandantenspalte
                    pass
            db.commit()


def _anlegen(haus, positionen, doc_type="sales_invoice", status="draft"):
    """``positionen`` = (Steuerschluessel, Satz, Menge, Preis)."""
    zeilen = []
    for nr, (code, satz, menge, preis) in enumerate(positionen, 1):
        zeile = {"article_number": f"A-{nr}", "quantity": menge, "unit_price": preis}
        if code is not None:
            zeile["tax_code"] = code
        if satz is not None:
            zeile["tax_rate"] = satz
        zeilen.append(zeile)
    return haus["client"].post("/docflow/", params={"tenant_id": haus["mandant"]}, json={
        "doc_type": doc_type, "doc_number": f"RE-{haus['lauf']}-{uuid.uuid4().hex[:4]}", "status": status,
        "customer_id": "kunde-1", "items": zeilen})


def _buchen(haus, doc_id: str):
    haus["client"].post(f"/docflow/{doc_id}/release", params={"tenant_id": haus["mandant"]},
                        json={"idempotency_key": f"frei-{doc_id}"})
    return haus["client"].post(f"/docflow/{doc_id}/post", params={"tenant_id": haus["mandant"]},
                               json={"idempotency_key": f"buchen-{doc_id}"})


def _buchung(mandant: str) -> list[tuple[str, Decimal, Decimal]]:
    with SessionLocal() as db:
        return [(z[0], Decimal(str(z[1])), Decimal(str(z[2]))) for z in db.execute(text(
            "SELECT k.account_number, l.debit, l.credit FROM domain_erp.journal_entry_lines l "
            "JOIN domain_erp.chart_of_accounts k ON k.id = l.account_id "
            "JOIN domain_erp.journal_entries e ON e.id = l.journal_entry_id "
            "WHERE e.tenant_id = :t ORDER BY k.account_number"), {"t": mandant}).fetchall()]


def _status(doc_id: str) -> str:
    with SessionLocal() as db:
        return db.execute(text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"), {"id": doc_id}).scalar()


# --- Die Position nennt den Schluessel ----------------------------------------------------------

def test_der_satz_der_position_kommt_aus_dem_steuerschluessel(haus):
    antwort = _anlegen(haus, [("3", None, 2, 500), ("2", None, 1, 200)])
    assert antwort.status_code == 200, antwort.text
    beleg = antwort.json()
    assert [(z["tax_code"], z["tax_rate"], z["line_total_tax"]) for z in beleg["items"]] == [("3", 19.0, 190.0), ("2", 7.0, 14.0)]
    assert (beleg["total_net"], beleg["total_tax"], beleg["total_gross"]) == (1200.0, 204.0, 1404.0)


@pytest.mark.parametrize("position,meldung", [
    (("3", 7, 1, 100), "Position 1: Steuersatz 7 % widerspricht dem Steuerschlüssel 3 (19 %)"),
    (("9", None, 1, 100), "Position 1: Steuerschlüssel 9 ist für Verkaufsbelege nicht bekannt oder nicht gültig"),
    (("77", None, 1, 100), "Steuerschlüssel 77 ist für Verkaufsbelege nicht bekannt"),
])
def test_ein_unpassender_schluessel_wird_schon_beim_speichern_abgelehnt(haus, position, meldung):
    antwort = _anlegen(haus, [position])
    assert antwort.status_code in (400, 422), antwort.text
    assert meldung in antwort.text
    with SessionLocal() as db:
        assert db.execute(text(
            "SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id = :t"), {"t": haus["mandant"]}).scalar() == 0


def test_aendern_ersetzt_die_positionen_mit_dem_neuen_schluessel(haus):
    doc_id = _anlegen(haus, [("3", None, 1, 100)]).json()["id"]
    antwort = haus["client"].put(f"/docflow/{doc_id}", params={"tenant_id": haus["mandant"]}, json={
        "items": [{"article_number": "A-1", "quantity": 1, "unit_price": 100, "tax_code": "2"}]})
    assert antwort.status_code == 200, antwort.text
    assert [(z["tax_code"], z["tax_rate"]) for z in antwort.json()["items"]] == [("2", 7.0)]
    assert antwort.json()["total_gross"] == 107.0


# --- Finance bucht je Schluessel ----------------------------------------------------------------

def test_rechnung_bucht_erloes_und_steuer_je_steuerschluessel(haus):
    doc_id = _anlegen(haus, [("3", None, 2, 500), ("2", None, 1, 200)]).json()["id"]
    antwort = _buchen(haus, doc_id)
    assert antwort.status_code == 200, antwort.text
    assert _buchung(haus["mandant"]) == [
        ("1400", Decimal("1404.00"), Decimal("0.00")),
        ("1771", Decimal("0.00"), Decimal("14.00")),
        ("1776", Decimal("0.00"), Decimal("190.00")),
        ("8300", Decimal("0.00"), Decimal("200.00")),
        ("8400", Decimal("0.00"), Decimal("1000.00")),
    ]
    assert _status(doc_id) == "posted"


def test_beleg_und_buchung_stimmen_auf_den_cent(haus):
    """Drei Positionen zu 0,33 € und 19 %: je Position 0,06 € Steuer — der Beleg sagt 0,18 €, und so wird gebucht."""
    beleg = _anlegen(haus, [("3", None, 1, 0.33)] * 3).json()
    assert (beleg["total_net"], beleg["total_tax"], beleg["total_gross"]) == (0.99, 0.18, 1.17)
    assert _buchen(haus, beleg["id"]).status_code == 200
    assert _buchung(haus["mandant"]) == [
        ("1400", Decimal("1.17"), Decimal("0.00")),
        ("1776", Decimal("0.00"), Decimal("0.18")),
        ("8400", Decimal("0.00"), Decimal("0.99")),
    ]


@pytest.mark.parametrize("positionen,meldung", [
    # Ein Satz allein genuegt nicht — bis zum 13.10.2026 wurde so gebucht, alles auf 8400 und 1776.
    ([(None, 19, 1, 100)], "Position 1 hat keinen Steuerschlüssel"),
    ([("3", None, 1, 100), (None, 7, 1, 50)], "Position 2 hat keinen Steuerschlüssel"),
    ([(None, None, 1, 100)], "Position 1 hat keinen Steuerschlüssel"),
])
def test_ohne_steuerschluessel_wird_gespeichert_aber_nicht_gebucht(haus, positionen, meldung):
    angelegt = _anlegen(haus, positionen)
    assert angelegt.status_code == 200, angelegt.text
    antwort = _buchen(haus, angelegt.json()["id"])
    assert antwort.status_code == 409, antwort.text
    assert "nicht gebucht, bitte prüfen" in antwort.json()["detail"] and meldung in antwort.json()["detail"]
    assert _buchung(haus["mandant"]) == []
    # Der Belegstatus ist pruefbar: nicht „gebucht“.
    assert _status(angelegt.json()["id"]) != "posted"


def test_umwandeln_nimmt_den_steuerschluessel_mit(haus):
    auftrag = _anlegen(haus, [("2", None, 4, 50)], doc_type="sales_order").json()
    haus["client"].post(f"/docflow/{auftrag['id']}/release", params={"tenant_id": haus["mandant"]},
                        json={"idempotency_key": f"frei-{auftrag['id']}"})
    antwort = haus["client"].post(f"/docflow/{auftrag['id']}/convert", params={"tenant_id": haus["mandant"]}, json={
        "target_doc_type": "sales_invoice", "idempotency_key": f"wandeln-{auftrag['id']}"})
    assert antwort.status_code == 200, antwort.text
    with SessionLocal() as db:
        zeilen = db.execute(text(
            "SELECT i.tax_code, i.tax_rate FROM domain_docflow.document_items i "
            "JOIN domain_docflow.document_headers h ON h.id = i.header_id "
            "WHERE h.tenant_id = :t AND h.doc_type = 'sales_invoice'"), {"t": haus["mandant"]}).fetchall()
    assert [(z[0], Decimal(str(z[1]))) for z in zeilen] == [("2", Decimal("7"))]
