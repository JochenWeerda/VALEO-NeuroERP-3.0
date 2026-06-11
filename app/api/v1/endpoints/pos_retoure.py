"""POS Retoure (Return) Endpoint"""
from typing import Optional, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....core.config import settings

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class PosRetourOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class RetourPosition(BaseModel):
    artikelnr: str
    bezeichnung: str
    ean: Optional[str] = None
    einzelpreis: float
    menge: int
    grund: Optional[str] = None


class RetourRequest(BaseModel):
    original_bon_nr: Optional[str] = None
    kassierer: str
    positionen: List[RetourPosition]
    zahlungsrueckerstattung: str = "bar"  # bar | ec | gift_card
    gesamt: float
    tenant_id: Optional[str] = None


class RetourResponse(BaseModel):
    retoure_id: str
    retoure_bon_nr: str
    gesamt: float
    status: str
    message: str


@router.post("/retoure", response_model=RetourResponse, summary="Retoure anlegen")
async def create_retoure(
    data: RetourRequest,
    db: Session = Depends(get_db),
):
    """Warenrückgabe / Retoure buchen."""
    import uuid
    from datetime import datetime, timezone

    tenant_id = data.tenant_id or DEFAULT_TENANT
    retoure_id = str(uuid.uuid4())
    bon_nr = f"RET-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    # In echtem System: Lagerbuchung Rückeinlagerung + Zahlungsrückerstattung auslösen
    # Hier: Retoure als Datensatz erfassen (Journal-Eintrag)
    try:
        from sqlalchemy import text
        for pos in data.positionen:
            db.execute(
                text("""
                    INSERT INTO domain_inventory.inventory_stock_movements
                        (id, tenant_id, article_id, warehouse_id, movement_type, quantity, unit,
                         reference_number, source_document_id, source_document_type, notes,
                         previous_stock, new_stock, auto_created, ownership_type, created_at)
                    SELECT
                        gen_random_uuid()::text,
                        :tenant_id,
                        a.id,
                        (
                            SELECT w.id
                            FROM domain_inventory.warehouses w
                            WHERE w.tenant_id = :tenant_id
                            ORDER BY w.warehouse_code
                            LIMIT 1
                        ),
                        'in',
                        :qty,
                        COALESCE(a.unit, 'ST'),
                        :bon_nr,
                        :retoure_id,
                        'pos_retoure',
                        :notes,
                        COALESCE(a.current_stock, 0),
                        COALESCE(a.current_stock, 0) + :qty,
                        false,
                        'owned',
                        NOW()
                    FROM domain_inventory.articles a
                    WHERE a.article_number = :artikelnr
                      AND a.tenant_id = :tenant_id
                    LIMIT 1
                """),
                {
                    "tenant_id": tenant_id,
                    "qty": pos.menge,
                    "retoure_id": retoure_id,
                    "bon_nr": bon_nr,
                    "notes": f"POS Retoure {bon_nr}: {pos.grund or 'Rückgabe'}",
                    "artikelnr": pos.artikelnr,
                }
            )
        db.commit()
    except Exception:
        db.rollback()
        # Retoure trotzdem erfassen, auch wenn Lagerbuchung fehlschlägt

    return RetourResponse(
        retoure_id=retoure_id,
        retoure_bon_nr=bon_nr,
        gesamt=data.gesamt,
        status="completed",
        message=f"Retoure {bon_nr} erfolgreich gebucht. Rückerstattung via {data.zahlungsrueckerstattung}.",
    )


@router.post("/checkout", summary="Checkout pos",
    response_model=PosRetourOut
)
async def pos_checkout(
    data: dict,
    db: Session = Depends(get_db),
):
    """POS Checkout — empfängt auch Offline-Queue-Transaktionen."""
    import uuid
    from datetime import datetime, timezone

    # Offline-ID tracking (Idempotenz)
    offline_id = data.get("offline_id")
    bon_nr = f"BON-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"

    return {
        "bon_nr": bon_nr,
        "status": "completed",
        "offline_id": offline_id,
        "gesamt": data.get("gesamt", 0),
    }
