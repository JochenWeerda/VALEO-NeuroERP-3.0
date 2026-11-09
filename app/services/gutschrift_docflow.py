"""Verkaufsgutschrift in DocFlow (BELEG-052, 09.11.2026: DocFlow einziger Belegspeicher).

Bis dahin fuehrte ``domain_sales.sales_credit_notes`` eigene Gutschriften mit eigener Buchung. DocFlow bucht die
Belegart ``sales_credit_memo`` selbst (``finance_belegbuchung.buche_verkaufsgutschrift``: Erloes netto und
Umsatzsteuer je Steuerschluessel im Soll, Forderung brutto im Haben, offener Posten der Bezugsrechnung gemindert).
Dieses Modul gibt den Agentenwerkzeugen ``sales.gutschrift.*`` dieselben drei Schritte auf DocFlow:

* ``lege_entwurf_an``: Entwurf mit Positionen und Steuerschluessel je Position (kein Satz, keine Vorgabe 19 %).
* ``vorschau``: was gebucht wuerde - oder der Pruefgrund (fehlender/unbekannter Schluessel, Widerspruch, Konto).
* ``buche``: die Buchung ueber ``DocflowService.post_document`` (dieselbe Pruefung, dieselbe Freigabe-Engine).
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.finance_belegbuchung import FORDERUNGEN as FORDERUNGSKONTO

QUELLE = "gutschrift"
ART = "sales_credit_memo"


def _kopf(db: Session, tenant: str, doc_id: str) -> Optional[dict[str, Any]]:
    zeile = db.execute(text(
        "SELECT id, doc_number, status, customer_id, source_ref, total_net, total_tax, total_gross "
        "FROM domain_docflow.document_headers WHERE tenant_id = :t AND id = :i AND doc_type = :a "
        "AND deleted_at IS NULL"), {"t": tenant, "i": doc_id, "a": ART}).mappings().first()
    return dict(zeile) if zeile else None


def lege_entwurf_an(db: Session, tenant: str, *, nummer: str, kunde: str, rechnung: Optional[str],
                    zeilen: list[dict[str, Any]], akteur: str, idempotenz: Optional[str] = None) -> str:
    """Gutschrift-Entwurf in DocFlow; die Nummer der Gutschrift je Mandant nur einmal (409)."""
    from app.services.beleg_anlage import Position, lege_beleg_an

    if db.execute(text("SELECT 1 FROM domain_docflow.document_headers WHERE tenant_id = :t AND doc_type = :a "
                       "AND source_system = :q AND source_ref = :n AND deleted_at IS NULL"),
                  {"t": tenant, "a": ART, "q": QUELLE, "n": nummer}).first():
        raise HTTPException(409, f"Credit note number {nummer} already exists")
    kunden_id = db.execute(text("SELECT id::text FROM domain_crm.customers WHERE tenant_id = :t AND "
                                "(id::text = :k OR customer_number = :k) LIMIT 1"), {"t": tenant, "k": kunde}).scalar()
    if kunden_id is None:
        raise HTTPException(422, f"Unknown customer {kunde}")
    beleg_id = lege_beleg_an(
        db, tenant, ART, partner_id=kunden_id, quelle=QUELLE, referenz=nummer, entwurf_nr=nummer, akteur=akteur,
        idempotenz=idempotenz,
        positionen=[Position(artikel_nr="GUTSCHRIFT", bezeichnung=str(z["description"])[:500],
                             menge=float(z["quantity"]), einzelpreis=float(z["unit_price"]),
                             steuerschluessel=(str(z.get("tax_code") or "").strip() or None)) for z in zeilen])
    if rechnung:
        bezug = db.execute(text(
            "SELECT id FROM domain_docflow.document_headers WHERE tenant_id = :t AND doc_type = 'sales_invoice' "
            "AND doc_number = :n AND deleted_at IS NULL LIMIT 1"), {"t": tenant, "n": rechnung}).scalar()
        if bezug is not None and not db.execute(text(
                "SELECT 1 FROM domain_docflow.document_header_links WHERE tenant_id = :t AND to_header_id = :z "
                "AND relation_type = 'invoice_to_credit_memo'"), {"t": tenant, "z": beleg_id}).first():
            db.execute(text(
                "INSERT INTO domain_docflow.document_header_links (id, tenant_id, from_header_id, to_header_id, "
                "relation_type, created_at) VALUES (:id, :t, :f, :z, 'invoice_to_credit_memo', NOW())"),
                {"id": str(uuid4()), "t": tenant, "f": bezug, "z": beleg_id})
    return beleg_id


def vorschau(db: Session, tenant: str, doc_id: str, akteur: str = "vorschau") -> dict[str, Any]:
    """Was die Buchung schreiben wuerde. Laesst sich die Gutschrift nicht buchen: HTTP 409 mit dem Grund."""
    from app.core.exceptions import ConflictError
    from app.services.docflow_service import DocflowService

    kopf = _kopf(db, tenant, doc_id)
    if kopf is None:
        raise HTTPException(404, "Gutschrift nicht gefunden")
    if str(kopf["status"]) == "posted":
        raise HTTPException(409, "Gutschrift bereits gebucht")
    try:
        gruppen = DocflowService(db, tenant, akteur)._steuergruppen_der_rechnung(doc_id, str(kopf["doc_number"]))
    except ConflictError as fehler:
        raise HTTPException(409, str(fehler).replace("Rechnung", "Gutschrift", 1)) from fehler
    netto = sum((g.netto for g in gruppen), Decimal("0"))
    steuer = sum((g.steuer for g in gruppen), Decimal("0"))
    if netto + steuer <= 0:
        raise HTTPException(409, "Gutschrift nicht gebucht, bitte prüfen: Der Betrag der Gutschrift ist null.")
    zeilen: list[dict[str, Any]] = []
    for g in gruppen:
        zeilen.append({"text": f"Gutschrift Erlöskorrektur netto ({g.tax_code})", "konto": g.erloeskonto,
                       "soll": g.netto, "haben": Decimal("0"), "code": g.tax_code})
        if g.steuer > 0:
            zeilen.append({"text": f"Gutschrift Umsatzsteuerberichtigung ({g.tax_code})", "konto": g.steuerkonto,
                           "soll": g.steuer, "haben": Decimal("0"), "code": g.tax_code})
    zeilen.append({"text": "Gutschrift Forderungsminderung", "konto": FORDERUNGSKONTO, "soll": Decimal("0"),
                   "haben": netto + steuer, "code": None})
    return {"id": doc_id, "nummer": str(kopf["source_ref"] or kopf["doc_number"]), "netto": netto,
            "steuer": steuer, "brutto": netto + steuer, "zeilen": zeilen}


def buche(db: Session, tenant: str, doc_id: str, *, akteur: str, idempotenz: str) -> dict[str, Any]:
    """Bucht ueber DocFlow (Pruefung, Freigabe-Engine, Buchungsnachweis) - ohne die Einheit des Aufrufers zu beenden.

    ``post_document`` committet; im Savepoint gibt das nur den Savepoint frei. Der Aufrufer (MCP-Werkzeug mit
    Vorschlag, Audit und Ausfuehrungsnachweis) committet alles zusammen oder nichts.
    """
    from app.api.v1.schemas.docflow_schemas import DocflowPostRequest
    from app.services.docflow_service import DocflowService

    from app.core.exceptions import DomainError

    with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as innen:
        try:
            ergebnis = DocflowService(innen, tenant, akteur).post_document(
                doc_id, DocflowPostRequest(idempotency_key=idempotenz, posted_by=akteur))
        except DomainError as fehler:  # Pruefgrund oder Freigabe fehlt: als Antwort, nicht als 500
            raise HTTPException(409, str(fehler)) from fehler
        innen.commit()
    return ergebnis
