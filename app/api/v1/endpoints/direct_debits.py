"""
Direct debit endpoints used by finance UI masks.
"""

import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.tenant import get_tenant_id
from ....core.database import get_db

from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.api.v1.schemas.direct_debits_schemas import DirectDebitsOut


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/direct-debits", tags=["finance", "direct-debits"])


@router.get("", response_model=list[DirectDebitsOut], summary="Direct debits auflisten")
async def list_direct_debits(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lastschriftlaeufe aus direct_debit_items aggregiert nach run_id."""
    try:
        rows = db.execute(text("""
            SELECT
                run_id,
                COUNT(*) AS anzahl,
                SUM(amount) AS gesamtbetrag,
                MIN(created_at) AS erstellt_am,
                MAX(CASE WHEN status = 'exported' THEN 'exported'
                         WHEN status = 'pending' THEN 'pending'
                         ELSE 'draft' END) AS status
            FROM domain_shared.direct_debit_items
            WHERE tenant_id = :tid
            GROUP BY run_id
            ORDER BY MIN(created_at) DESC
            LIMIT 50
        """), {"tid": tenant_id}).fetchall()
        return [
            {
                "id": r.run_id,
                "laufnummer": r.run_id,
                "anzahlLastschriften": r.anzahl,
                "gesamtbetrag": float(r.gesamtbetrag or 0),
                "status": r.status or "draft",
                "erstellt_am": str(r.erstellt_am) if r.erstellt_am else None,
            }
            for r in rows
        ]
    except Exception as exc:
        # Keine leere Liste: "keine Laeufe" und "die Datenbank antwortet nicht"
        # sehen sonst gleich aus, und im zweiten Fall haelt ein Haus einen
        # faelligen Lastschriftlauf fuer erledigt.
        db.rollback()
        logger.exception("Lastschriftlaeufe nicht lesbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503, detail="Lastschriftlaeufe sind derzeit nicht abrufbar"
        ) from exc


@router.get("/new", response_model=DirectDebitsOut, summary="New direct debit template abrufen")
async def get_new_direct_debit_template(tenant_id: str = Depends(get_tenant_id)):
    """Return default values for direct debit create forms."""
    return {
        "id": None,
        "tenant_id": tenant_id,
        "laufnummer": "",
        "faelligkeitsdatum": date.today().isoformat(),
        "ausfuehrungsdatum": date.today().isoformat(),
        "sepaSchema": "CORE",
        "sequenzTyp": "RCUR",
        "glaeubigerId": "",
        "abbucherName": "",
        "anzahlLastschriften": 0,
        "gesamtbetrag": 0,
        "status": "draft",
        "lastschriften": [],
    }


# --------------- Pydantic Schemas ---------------
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from starlette.responses import Response
import uuid


class DirectDebitItemCreate(BaseModel):
    debitor_name: str
    iban: str
    bic: Optional[str] = None
    mandate_id: str
    amount: float
    verwendungszweck: Optional[str] = None


class DirectDebitRunCreate(BaseModel):
    faelligkeitsdatum: date
    ausfuehrungsdatum: date
    sepa_schema: str = "CORE"
    sequenz_typ: str = "RCUR"
    glaeubiger_id: str
    abbucher_name: str
    items: List[DirectDebitItemCreate]


# --------------- POST / DELETE ---------------


@router.post("", response_model=DirectDebitsOut, status_code=201, summary="Direct debit run anlegen")
async def create_direct_debit_run(
    body: DirectDebitRunCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Create a new direct debit run with items."""
    run_id = f"LS-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.utcnow()

    for item in body.items:
        db.execute(text("""
            INSERT INTO domain_shared.direct_debit_items
                (tenant_id, run_id, debitor_name, iban, bic, mandate_id, amount,
                 verwendungszweck, status, created_at)
            VALUES
                (:tid, :run_id, :debitor_name, :iban, :bic, :mandate_id, :amount,
                 :verwendungszweck, 'pending', :created_at)
        """), {
            "tid": tenant_id,
            "run_id": run_id,
            "debitor_name": item.debitor_name,
            "iban": item.iban,
            "bic": item.bic,
            "mandate_id": item.mandate_id,
            "amount": item.amount,
            "verwendungszweck": item.verwendungszweck,
            "created_at": now,
        })
    db.commit()

    return {
        "id": run_id,
        "laufnummer": run_id,
        "anzahlLastschriften": len(body.items),
        "gesamtbetrag": sum(i.amount for i in body.items),
        "status": "pending",
        "erstellt_am": now.isoformat(),
    }


@router.get("/{run_id}", response_model=DirectDebitsOut, summary="Direct debit run abrufen")
async def get_direct_debit_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Einzelnen Lastschriftlauf mit Positionen abrufen."""
    try:
        rows = db.execute(text("""
            SELECT run_id, debitor_name, iban, bic, mandate_id, amount,
                   verwendungszweck, status, created_at
            FROM domain_shared.direct_debit_items
            WHERE tenant_id = :tid AND run_id = :run_id
            ORDER BY created_at
        """), {"tid": tenant_id, "run_id": run_id}).fetchall()
    except Exception as exc:
        db.rollback()
        logger.exception("Lastschriftlauf %s nicht lesbar", run_id)
        raise HTTPException(
            status_code=503, detail="Lastschriftlauf ist derzeit nicht abrufbar"
        ) from exc
    if not rows:
        raise HTTPException(status_code=404, detail="Lastschriftlauf nicht gefunden")
    items = [
        {
            "debitor_name": r.debitor_name,
            "iban": r.iban,
            "bic": r.bic,
            "mandate_id": r.mandate_id,
            "amount": float(r.amount),
            "verwendungszweck": r.verwendungszweck,
            "status": r.status,
        }
        for r in rows
    ]
    return {
        "id": run_id,
        "laufnummer": run_id,
        "anzahlLastschriften": len(items),
        "gesamtbetrag": sum(i["amount"] for i in items),
        "status": rows[0].status,
        "erstellt_am": str(rows[0].created_at) if rows[0].created_at else None,
        "lastschriften": items,
    }


@router.post("/{run_id}/export", response_model=StatusResponse, summary="Direct debit run exportieren")
async def export_direct_debit_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Lastschriftlauf exportieren — setzt alle pending Positionen auf 'exported'."""
    try:
        result = db.execute(text("""
            UPDATE domain_shared.direct_debit_items
            SET status = 'exported'
            WHERE tenant_id = :tid AND run_id = :run_id AND status = 'pending'
        """), {"tid": tenant_id, "run_id": run_id})
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Lauf nicht gefunden oder bereits exportiert")
    return {"ok": True, "run_id": run_id, "exported_items": result.rowcount}


@router.delete("/{run_id}", response_class=Response, status_code=204, response_model=None, summary="Direct debit run stornieren")
async def cancel_direct_debit_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    """Cancel a direct debit run by setting all its items to 'cancelled'."""
    result = db.execute(text("""
        UPDATE domain_shared.direct_debit_items
        SET status = 'cancelled'
        WHERE tenant_id = :tid AND run_id = :run_id AND status != 'exported'
    """), {"tid": tenant_id, "run_id": run_id})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Lastschriftlauf nicht gefunden oder bereits exportiert")
    return Response(status_code=204)
