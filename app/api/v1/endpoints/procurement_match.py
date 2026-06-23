"""Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

Bestellung ↔ Wareneingang (Basis; Rechnungs-Stufe folgt). Read-only: Mengen-/
Wertabweichung und Lücken je Bestellung sichtbar machen.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
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


@router.get("/match/orders", response_model=dict[str, Any], summary="Bestellungen mit Match-Übersicht (Picker)")
def list_orders(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ProcurementMatchService(db, tenant_id).list_orders(limit=limit)}


@router.get("/match", response_model=dict[str, Any], summary="3-Wege-Match je Bestellung (Bestellung ↔ Wareneingang)")
def match(
    bestellung: str = Query(..., description="Bestellnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).match(bestellung)


@router.get("/match/three-way", response_model=dict[str, Any], summary="3-Wege-Match inkl. Eingangsrechnung")
def match_three_way(
    bestellung: str = Query(..., description="Bestellnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).match_three_way(bestellung)


@router.get("/match/follow-up", response_model=dict[str, Any], summary="Folgeaktionen je Bestellung (append-only)")
def list_follow_ups(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {
        "items": ProcurementMatchService(db, tenant_id).list_follow_ups(bestellung),
    }


@router.post("/match/follow-up", response_model=dict[str, Any], summary="Folgeaktion erfassen (append-only)", status_code=201)
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


@router.get("/match/ers/preview", response_model=dict[str, Any], summary="ERS-Gutschrift-Vorschau je Bestellung")
def preview_ers(
    bestellung: str = Query(..., description="Bestellnummer"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).preview_ers(bestellung)


@router.get("/match/ers", response_model=dict[str, Any], summary="Erfasste ERS-Gutschriften je Bestellung")
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


def _decimal_from(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _sum_position_value(positionen: list[dict[str, Any]], field: str) -> Decimal:
    return sum((_decimal_from(pos.get(field)) for pos in positionen), Decimal("0"))


def _max_abs_position_delta_pct(positionen: list[dict[str, Any]]) -> Decimal:
    deltas = [_decimal_from(pos.get("abweichung_pct")).copy_abs() for pos in positionen]
    return max(deltas, default=Decimal("0"))


@router.post("/match/auto", response_model=dict[str, Any], summary="PROC-3WM-001: 3-Wege-Match ausführen und Ergebnis persistieren", status_code=201)
def auto_match_and_persist(
    body: AutoMatchIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Führt den 3-Wege-Match aus und speichert das Ergebnis in procurement_match_results."""
    from sqlalchemy import text

    service = ProcurementMatchService(db, tenant_id)
    result = service.match_three_way(body.bestellnummer)
    if not result.get("found", False):
        raise HTTPException(status_code=404, detail=result.get("detail") or "Bestellung nicht gefunden")

    three_way = result.get("three_way", {})
    positionen = result.get("positionen") or []
    invoices = result.get("rechnungen") or []
    goods_receipts = result.get("wareneingaenge") or []
    qty_delta_pct = _max_abs_position_delta_pct(positionen)
    value_delta_pct = _decimal_from(three_way.get("abweichung_pct")).copy_abs()
    qty_tolerance_pct = _decimal_from(body.qty_tolerance_pct)
    price_tolerance_pct = _decimal_from(body.price_tolerance_pct)

    missing_context: list[str] = []
    if not goods_receipts:
        missing_context.append("Wareneingang")
    if not invoices:
        missing_context.append("Eingangsrechnung")

    qty_ok = qty_delta_pct <= qty_tolerance_pct
    value_ok = value_delta_pct <= price_tolerance_pct
    if missing_context:
        match_status = "PENDING"
    elif qty_ok and value_ok:
        match_status = "MATCH_OK"
    else:
        match_status = "MISMATCH"

    discrepancy_parts: list[str] = []
    if missing_context:
        discrepancy_parts.append(f"Offen: {', '.join(missing_context)} fehlt")
    if not qty_ok:
        discrepancy_parts.append(f"Mengenabweichung {qty_delta_pct}% > Toleranz {qty_tolerance_pct}%")
    if not value_ok:
        discrepancy_parts.append(f"Wertabweichung {value_delta_pct}% > Toleranz {price_tolerance_pct}%")
    ausnahmen = result.get("ausnahmen") or []
    if ausnahmen:
        discrepancy_parts.extend(a.get("text", "") for a in ausnahmen[:3] if a.get("text"))
    discrepancy = "; ".join(discrepancy_parts) or None

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
                "qty_po": _sum_position_value(positionen, "bestellt"),
                "qty_gr": _sum_position_value(positionen, "geliefert"),
                "qty_ap": None,
                "price_po": three_way.get("bestellt_wert"),
                "price_ap": three_way.get("fakturiert_netto"),
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
        "drei_wege_abgeglichen": match_status == "MATCH_OK",
        "discrepancy_reason": discrepancy,
        "tolerance_check": {
            "qty_delta_pct": float(qty_delta_pct),
            "qty_tolerance_pct": body.qty_tolerance_pct,
            "qty_ok": qty_ok,
            "value_delta_pct": float(value_delta_pct),
            "price_tolerance_pct": body.price_tolerance_pct,
            "value_ok": value_ok,
            "missing_context": missing_context,
        },
        "detail": result,
    }


@router.get("/match/results", response_model=dict[str, Any], summary="Gespeicherte Match-Ergebnisse abrufen")
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
        text(f"SELECT * FROM domain_procurement.procurement_match_results WHERE {where} ORDER BY created_at DESC LIMIT :limit"),  # nosec S608 -- reviewed-safe: where fragments are code-controlled, values parameterized
        params,
    ).mappings().all()
    return {"items": [dict(r) for r in rows]}


@router.post("/match/ers", response_model=dict[str, Any], summary="ERS-Gutschrift aus Match-Abweichung erzeugen", status_code=201)
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


# ---------------------------------------------------------------------------
# DOM-PROC-004: Bestellung-Lifecycle / Wareneingang / Rechnungsprüfung
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _BM
from typing import Optional as _Opt


class BestellungTransitionIn(_BM):
    new_status: str
    operator: _Opt[str] = "system"
    reason: _Opt[str] = None


class WareneingangIn(_BM):
    menge_erhalten: float
    einheit: str
    lager_id: str
    operator: _Opt[str] = "system"
    qs_status: _Opt[str] = "AUSSTEHEND"


class QSUpdateIn(_BM):
    qs_status: str
    operator: _Opt[str] = "system"


class RechnungspruefungIn(_BM):
    rechnungs_nr: str
    rechnungs_betrag_eur: float
    bestell_preis_eur: float
    we_menge: float
    schwelle_pct: _Opt[float] = 3.0


class RechnungsFreigabeIn(_BM):
    entscheidung: str
    operator: str
    grund: _Opt[str] = None


@router.post("/bestellungen/{bestellung_id}/transition", response_model=dict[str, Any], summary="Bestellungs-Status wechseln")
def bestellung_transition_endpoint(
    bestellung_id: str,
    body: BestellungTransitionIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.proc_bestellung_lifecycle_service import transition_bestellung_status, BestellungLifecycleError
    tenant_id = x_tenant_id or "default"
    try:
        return transition_bestellung_status(db, bestellung_id, tenant_id, body.new_status,
                                             body.operator or "system", body.reason)
    except BestellungLifecycleError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/bestellungen/{bestellung_id}/wareneingang", response_model=dict[str, Any], status_code=201, summary="Wareneingang buchen")
def buche_wareneingang_endpoint(
    bestellung_id: str,
    body: WareneingangIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.proc_wareneingang_service import buche_wareneingang, WareneingangError
    tenant_id = x_tenant_id or "default"
    try:
        return buche_wareneingang(db, bestellung_id, tenant_id, body.menge_erhalten,
                                   body.einheit, body.lager_id, body.operator or "system",
                                   body.qs_status or "AUSSTEHEND")
    except WareneingangError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/wareneingaenge/{we_id}/qs", response_model=dict[str, Any], summary="QS-Status eines Wareneingangs aktualisieren")
def update_we_qs_endpoint(
    we_id: str,
    body: QSUpdateIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.proc_wareneingang_service import update_qs_status, WareneingangError
    tenant_id = x_tenant_id or "default"
    try:
        return update_qs_status(db, we_id, tenant_id, body.qs_status, body.operator or "system")
    except WareneingangError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/bestellungen/{bestellung_id}/rechnungspruefung", response_model=dict[str, Any], status_code=201, summary="Rechnungsprüfung (response_model=dict[str, Any], 3-Way-Match)")
def rechnungspruefung_endpoint(
    bestellung_id: str,
    body: RechnungspruefungIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.proc_rechnungspruefung_service import pruefe_rechnung, RechnungspruefungError
    tenant_id = x_tenant_id or "default"
    try:
        return pruefe_rechnung(db, bestellung_id, tenant_id, body.rechnungs_nr,
                                body.rechnungs_betrag_eur, body.bestell_preis_eur,
                                body.we_menge, body.schwelle_pct or 3.0)
    except RechnungspruefungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/rechnungspruefungen/{pruefung_id}/freigabe", response_model=dict[str, Any], summary="Rechnungsprüfung manuell freigeben")
def rechnungsfreigabe_endpoint(
    pruefung_id: str,
    body: RechnungsFreigabeIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.proc_rechnungspruefung_service import freigabe_rechnungspruefung, RechnungspruefungError
    tenant_id = x_tenant_id or "default"
    try:
        return freigabe_rechnungspruefung(db, pruefung_id, tenant_id, body.entscheidung,
                                           body.operator, body.grund)
    except RechnungspruefungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
