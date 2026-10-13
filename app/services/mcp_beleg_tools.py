"""Lesende MCP-Werkzeuge fuer Belege (BELEG-013).

Ein Agent liest denselben Beleg wie die Maske: ueber den Belegvertrag, nicht ueber Tabellen. Die Werkzeuge
schreiben nichts; der Mandant kommt aus der geprueften Anmeldung (``execute_mcp_tool``).
"""
from __future__ import annotations

from typing import Any, Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.belegkommandos import BELEGKOMMANDOS, als_dict
from app.core.belegvertrag import BELEGARTEN, PREISFELDER, STATUS, VERTRAGSVERSION
from app.services.docflow_belegadapter import lies_beleg
from app.services.docflow_service import DocflowService

_Belegart = Literal[
    "sales_offer", "sales_order", "sales_delivery", "sales_invoice", "sales_credit_memo",
    "purchase_order", "goods_receipt", "purchase_invoice", "purchase_credit_memo",
]


class _Eingabe(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class BelegArtenInput(_Eingabe):
    pass


class BelegSuchenInput(_Eingabe):
    belegart: _Belegart | None = None
    status: Literal["draft", "open", "released", "posted", "reversed", "cancelled"] | None = None
    beleg_nr: str | None = Field(default=None, min_length=1, max_length=64)
    partner_nr: str | None = Field(default=None, min_length=1, max_length=64)
    limit: int = Field(default=20, ge=1, le=50)


class BelegLesenInput(_Eingabe):
    belegart: _Belegart
    beleg_id: str = Field(min_length=1, max_length=64)


def _eingabe(modell: type[BaseModel], request: Any, was: str) -> Any:
    try:
        opened = modell.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, f"Invalid {was} parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, f"{request.tool_name} does not support propose")
    return opened


def beleg_arten(db: Session, request: Any, actor: str, tenant: str) -> dict:
    """Welche Belegarten es gibt, was sie tragen und welche Kommandos es fuer Belege gibt."""
    del db, actor, tenant
    _eingabe(BelegArtenInput, request, "document type")
    return {
        "success": True,
        "mode": request.mode,
        "vertragsversion": VERTRAGSVERSION,
        "status": list(STATUS),
        "preisfelder": list(PREISFELDER),
        "belegarten": [
            {
                "belegart": v.belegart, "bezeichnung": v.bezeichnung, "partnerrolle": v.partnerrolle,
                "steuerrichtung": v.richtung, "mit_preisen": v.mit_preisen, "finance_bucht": v.bucht,
                "folgebelege": list(v.folgebelege),
            }
            for v in BELEGARTEN.values()
        ],
        "kommandos": [als_dict(k) for k in BELEGKOMMANDOS.values()],
    }


def beleg_suchen(db: Session, request: Any, actor: str, tenant: str) -> dict:
    del actor
    opened = _eingabe(BelegSuchenInput, request, "document search")
    try:
        zeilen = db.execute(
            text(
                """
                SELECT id, doc_type, doc_number, status, document_date, customer_id, supplier_id, currency, total_gross
                FROM domain_docflow.document_headers
                WHERE tenant_id = :tenant AND deleted_at IS NULL
                  AND doc_type = ANY(:arten)
                  AND (CAST(:status AS text) IS NULL OR status = :status)
                  AND (CAST(:nr AS text) IS NULL OR doc_number ILIKE '%' || :nr || '%')
                  AND (CAST(:partner AS text) IS NULL OR customer_id = :partner OR supplier_id = :partner)
                ORDER BY document_date DESC, doc_number DESC
                LIMIT :lim
                """
            ),
            {
                "tenant": tenant, "arten": [opened.belegart] if opened.belegart else sorted(BELEGARTEN),
                "status": opened.status, "nr": opened.beleg_nr, "partner": opened.partner_nr, "lim": opened.limit,
            },
        ).mappings().all()
        items = []
        for z in zeilen:
            variante = BELEGARTEN[str(z["doc_type"])]
            datum = z["document_date"]
            items.append({
                "beleg_id": str(z["id"]),
                "belegart": variante.belegart,
                "bezeichnung": variante.bezeichnung,
                "beleg_nr": str(z["doc_number"]),
                "status": str(z["status"]),
                "belegdatum": (datum.date() if hasattr(datum, "date") else datum).isoformat(),
                "partner_nr": z["supplier_id"] if variante.partnerrolle == "lieferant" else z["customer_id"],
                # Ohne Preise in der Variante auch kein Betrag in der Trefferliste.
                "brutto": str(z["total_gross"]) if variante.mit_preisen else None,
                "waehrung": str(z["currency"] or "EUR") if variante.mit_preisen else None,
            })
        result = {"success": True, "mode": request.mode, "items": items, "count": len(items)}
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def beleg_lesen(db: Session, request: Any, actor: str, tenant: str) -> dict:
    del actor
    opened = _eingabe(BelegLesenInput, request, "document read")
    try:
        beleg = lies_beleg(DocflowService(db, tenant), opened.beleg_id)
        if beleg is None or beleg.belegart != opened.belegart:
            raise HTTPException(404, "Document not found in the authenticated tenant")
        result = {"success": True, "mode": request.mode, "beleg": beleg.model_dump(mode="json")}
        db.rollback()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc
