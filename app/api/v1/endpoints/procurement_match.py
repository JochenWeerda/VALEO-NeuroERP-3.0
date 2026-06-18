"""Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

Bestellung ↔ Wareneingang (Basis; Rechnungs-Stufe folgt). Read-only: Mengen-/
Wertabweichung und Lücken je Bestellung sichtbar machen.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.procurement_match_service import ProcurementMatchService

router = APIRouter(prefix="/procurement", tags=["procurement", "einkauf"])


class FollowUpIn(BaseModel):
    bestellnummer: str = Field(..., min_length=1)
    action_type: str = Field(..., description="nachforderung | reklamation | eskalation | freigabe")
    grund: str = Field(..., min_length=3)
    ausnahme_code: Optional[str] = None
    created_by: Optional[str] = None


class ErsCreditIn(BaseModel):
    bestellnummer: str = Field(..., min_length=1)
    grund: Optional[str] = None
    created_by: Optional[str] = None


@router.get("/match/orders", summary="Bestellungen mit Match-Übersicht (Picker)")
def list_orders(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ProcurementMatchService(db, tenant_id).list_orders(limit=limit)}


@router.get("/match", summary="3-Wege-Match je Bestellung (Bestellung ↔ Wareneingang)")
def match(
    bestellung: str = Query(..., description="Bestellnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).match(bestellung)


@router.get("/match/three-way", summary="3-Wege-Match inkl. Eingangsrechnung")
def match_three_way(
    bestellung: str = Query(..., description="Bestellnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).match_three_way(bestellung)


@router.get("/match/follow-up", summary="Folgeaktionen je Bestellung (append-only)")
def list_follow_ups(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {
        "items": ProcurementMatchService(db, tenant_id).list_follow_ups(bestellung),
    }


@router.post("/match/follow-up", summary="Folgeaktion erfassen (append-only)", status_code=201)
def create_follow_up(
    body: FollowUpIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ProcurementMatchService(db, tenant_id)
    try:
        return service.create_follow_up(
            bestellnummer=body.bestellnummer,
            action_type=body.action_type,
            grund=body.grund,
            ausnahme_code=body.ausnahme_code,
            created_by=body.created_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Folgeaktion konnte nicht gespeichert werden: {exc}") from exc


@router.get("/match/ers/preview", summary="ERS-Gutschrift-Vorschau je Bestellung")
def preview_ers(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).preview_ers(bestellung)


@router.get("/match/ers", summary="Erfasste ERS-Gutschriften je Bestellung")
def list_ers_credits(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {
        "items": ProcurementMatchService(db, tenant_id).list_ers_credits(bestellung),
    }


class AutoMatchIn(BaseModel):
    bestellnummer: str = Field(..., min_length=1)
    po_id: Optional[str] = None
    gr_id: Optional[str] = None
    ap_invoice_id: Optional[str] = None
    qty_tolerance_pct: float = Field(default=2.0, ge=0, le=50)
    price_tolerance_pct: float = Field(default=1.0, ge=0, le=50)
    matched_by: Optional[str] = None


@router.post("/match/auto", summary="PROC-3WM-001: 3-Wege-Match ausführen und Ergebnis persistieren", status_code=201)
def auto_match_and_persist(
    body: AutoMatchIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Führt den 3-Wege-Match aus und speichert das Ergebnis in procurement_match_results."""
    from sqlalchemy import text
    from datetime import datetime, timezone

    service = ProcurementMatchService(db, tenant_id)
    result = service.match_three_way(body.bestellnummer)
    three_way = result.get("three_way", {})

    match_ok = three_way.get("drei_wege_abgeglichen", False)
    has_exception = result.get("summary", {}).get("hat_ausnahme", False)
    if match_ok:
        match_status = "MATCH_OK"
    elif has_exception:
        match_status = "MISMATCH"
    else:
        match_status = "PENDING"

    discrepancy = None
    ausnahmen = result.get("ausnahmen") or []
    if ausnahmen:
        discrepancy = "; ".join(a.get("text", "") for a in ausnahmen[:3])

    try:
        from app.core.uuid7 import uuid7
        match_id = str(uuid7())
        db.execute(
            text("""
                INSERT INTO domain_procurement.procurement_match_results
                    (id, tenant_id, po_id, gr_id, ap_invoice_id, match_status,
                     qty_po, qty_gr, qty_ap, price_po, price_ap,
                     qty_tolerance_pct, price_tolerance_pct,
                     discrepancy_reason, matched_by, matched_at)
                VALUES (:id, :tid, :po_id, :gr_id, :ap_id, :status,
                        :qty_po, :qty_gr, :qty_ap, :price_po, :price_ap,
                        :qty_tol, :price_tol, :discr, :by, NOW())
                ON CONFLICT DO NOTHING
            """),
            {
                "id": match_id, "tid": tenant_id,
                "po_id": body.po_id, "gr_id": body.gr_id, "ap_id": body.ap_invoice_id,
                "status": match_status,
                "qty_po": three_way.get("bestellt_wert"),
                "qty_gr": three_way.get("geliefert_wert"),
                "qty_ap": three_way.get("fakturiert_netto"),
                "price_po": None, "price_ap": None,
                "qty_tol": body.qty_tolerance_pct,
                "price_tol": body.price_tolerance_pct,
                "discr": discrepancy, "by": body.matched_by,
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, f"Match-Ergebnis konnte nicht gespeichert werden: {exc}") from exc

    return {
        "match_id": match_id,
        "match_status": match_status,
        "drei_wege_abgeglichen": match_ok,
        "discrepancy_reason": discrepancy,
        "detail": result,
    }


@router.get("/match/results", summary="Gespeicherte Match-Ergebnisse abrufen")
def list_match_results(
    po_id: Optional[str] = Query(None),
    match_status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    from sqlalchemy import text
    filters = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id, "limit": limit}
    if po_id:
        filters.append("po_id = :po_id")
        params["po_id"] = po_id
    if match_status:
        filters.append("match_status = :status")
        params["status"] = match_status
    where = " AND ".join(filters)
    rows = db.execute(
        text(f"SELECT * FROM domain_procurement.procurement_match_results WHERE {where} ORDER BY created_at DESC LIMIT :limit"),  # noqa: S608
        params,
    ).mappings().all()
    return {"items": [dict(r) for r in rows]}


@router.post("/match/ers", summary="ERS-Gutschrift aus Match-Abweichung erzeugen", status_code=201)
def create_ers_credit(
    body: ErsCreditIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ProcurementMatchService(db, tenant_id)
    try:
        return service.create_ers_credit(
            bestellnummer=body.bestellnummer,
            grund=body.grund,
            created_by=body.created_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"ERS-Gutschrift konnte nicht erzeugt werden: {exc}") from exc
