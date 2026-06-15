"""Sales Delivery Notes (Lieferscheine) CRUD endpoints."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
import json
from app.core.uuid7 import uuid7

from fastapi import Response, APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.tenant import get_tenant_id
from app.services.customer_sales_eligibility import assert_customer_allowed_for_delivery
from app.services.kontrakt_movement_sync import sync_movements_for_delivery_note
from app.services.sales_posting_service import SalesPostingService

from app.documents.router_helpers import get_repository, save_to_store

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.sales_delivery_notes_schemas import SalesDeliveryNotesOut


router = APIRouter(prefix="/sales/delivery-notes", tags=["sales", "delivery-notes"])


def _get_user_id_from_request(request: Request | None) -> str | None:
    if request is None:
        return None
    uid = request.headers.get("X-User-ID")
    if uid:
        return uid
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            import base64 as _b64
            import json as _json
            payload = auth[7:].split(".")[1]
            payload += "=" * (4 - len(payload) % 4)
            return _json.loads(_b64.urlsafe_b64decode(payload)).get("sub")
        except Exception:  # noqa: BLE001 — JWT decode failed; caller handles None return
            pass
    return None

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class DeliveryNotePositionBase(BaseModel):
    pos_nr: int = Field(ge=1)
    artikel_id: Optional[str] = None
    artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    bezeichnung2: Optional[str] = None
    menge: Decimal = Field(ge=Decimal("0"))
    einheit: Optional[str] = None
    listenpreis: Optional[Decimal] = None
    rabatt: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("100"))
    art: Optional[str] = None
    netto_preis: Optional[Decimal] = None
    netto_betrag: Optional[Decimal] = None
    niederlassung: Optional[int] = None
    lagerhalle: Optional[str] = None
    lagerfach: Optional[str] = None
    charge: Optional[str] = None
    serien_nr: Optional[str] = None
    erloskonto: Optional[str] = None
    mwst_prozent: Decimal = Field(default=Decimal("19"), ge=Decimal("0"), le=Decimal("100"))
    kontrakt_nr: Optional[str] = None
    skontierf: bool = False
    fremdware: bool = False
    gef_punkt: Optional[str] = None
    na_bio: Optional[str] = None
    muster_nr: Optional[str] = None
    strecke: Optional[str] = None
    zus_beleg: Optional[str] = None
    anerken: Optional[str] = None


class DeliveryNotePositionCreate(DeliveryNotePositionBase):
    pass


class DeliveryNotePosition(DeliveryNotePositionBase):
    id: str
    delivery_note_id: str
    created_at: datetime
    updated_at: datetime


class DeliveryNoteBase(BaseModel):
    customer_id: Optional[str] = None
    branch_id: Optional[str] = None
    sales_rep_id: Optional[str] = None
    operator_id: Optional[str] = None
    delivery_date: date
    delivery_time: Optional[time] = None
    cost_center_id: Optional[str] = None
    truck_number: Optional[int] = None
    is_credit_note: bool = False
    is_self_pickup: bool = False
    is_early_payment: bool = False
    reference_invoice_number: Optional[str] = None
    status: str = Field(default="draft")
    is_printed: bool = False
    is_delivered: bool = False
    invoice_number: Optional[str] = None
    sales_order_id: Optional[str] = None


class DeliveryNoteCreate(DeliveryNoteBase):
    positionen: list[DeliveryNotePositionCreate] = []


class DeliveryNoteUpdate(BaseModel):
    customer_id: Optional[str] = None
    branch_id: Optional[str] = None
    sales_rep_id: Optional[str] = None
    delivery_date: Optional[date] = None
    delivery_time: Optional[time] = None
    cost_center_id: Optional[str] = None
    truck_number: Optional[int] = None
    is_credit_note: Optional[bool] = None
    is_self_pickup: Optional[bool] = None
    is_early_payment: Optional[bool] = None
    reference_invoice_number: Optional[str] = None
    status: Optional[str] = None
    is_printed: Optional[bool] = None
    is_delivered: Optional[bool] = None
    invoice_number: Optional[str] = None
    positionen: Optional[list[DeliveryNotePositionCreate]] = None


class DeliveryNote(DeliveryNoteBase):
    id: str
    tenant_id: str
    delivery_note_number: str
    totals: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    positionen: list[DeliveryNotePosition] = []


def _generate_delivery_note_number(db: Session, tenant_id: str) -> str:
    """Generate unique delivery note number."""
    year = datetime.now().year
    # Get last number for this year
    result = db.execute(
        text("""
            SELECT delivery_note_number 
            FROM domain_sales.delivery_notes 
            WHERE tenant_id = :tenant_id 
            AND delivery_note_number LIKE :prefix
            ORDER BY delivery_note_number DESC 
            LIMIT 1
        """),
        {"tenant_id": tenant_id, "prefix": f"{year}%"}
    ).first()
    
    if result:
        last_num = result[0]
        try:
            # Extract number part (after year)
            num_part = int(last_num[len(str(year)):])
            next_num = num_part + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1
    
    return f"{year}{str(next_num).zfill(6)}"


def _get_delivery_note_or_404(db: Session, ls_id: str, tenant_id: str) -> dict:
    """Get delivery note or raise 404."""
    row = db.execute(
        text("""
            SELECT * FROM domain_sales.delivery_notes 
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": ls_id, "tenant_id": tenant_id}
    ).mappings().first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Delivery note not found")
    return dict(row)


def _list_positions(db: Session, delivery_note_id: str) -> list[dict]:
    """List all positions for a delivery note."""
    rows = db.execute(
        text("""
            SELECT * FROM domain_sales.delivery_note_positions 
            WHERE delivery_note_id = :id 
            ORDER BY pos_nr
        """),
        {"id": delivery_note_id}
    ).mappings().all()
    return [dict(row) for row in rows]


@router.post("", response_model=DeliveryNote, status_code=status.HTTP_201_CREATED, summary="Delivery note anlegen")
async def create_delivery_note(
    payload: DeliveryNoteCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a new delivery note."""
    if payload.customer_id:
        assert_customer_allowed_for_delivery(db, tenant_id, payload.customer_id)

    ls_id = uuid7()
    delivery_note_number = _generate_delivery_note_number(db, tenant_id)
    
    # Calculate totals
    netto = Decimal("0")
    mwst = Decimal("0")
    for pos in payload.positionen:
        listenpreis = pos.listenpreis or Decimal("0")
        rabatt = pos.rabatt or Decimal("0")
        menge = pos.menge
        mwst_prozent = pos.mwst_prozent or Decimal("19")
        
        netto_preis = listenpreis * (Decimal("1") - rabatt / Decimal("100"))
        netto_betrag = netto_preis * menge
        mwst_betrag = netto_betrag * mwst_prozent / Decimal("100")
        
        netto += netto_betrag
        mwst += mwst_betrag
    
    brutto = netto + mwst
    
    totals = {
        "netto": float(netto),
        "mwst": float(mwst),
        "brutto": float(brutto),
    }
    
    # Convert totals dict to JSON string for JSONB
    totals_json = json.dumps(totals)
    
    # Insert delivery note header
    db.execute(
        text("""
            INSERT INTO domain_sales.delivery_notes (
                id, tenant_id, delivery_note_number, customer_id, branch_id, sales_rep_id, operator_id,
                delivery_date, delivery_time, cost_center_id, truck_number,
                is_credit_note, is_self_pickup, is_early_payment, reference_invoice_number,
                status, is_printed, is_delivered, invoice_number, totals, sales_order_id,
                created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :delivery_note_number, :customer_id, :branch_id, :sales_rep_id, :operator_id,
                :delivery_date, :delivery_time, :cost_center_id, :truck_number,
                :is_credit_note, :is_self_pickup, :is_early_payment, :reference_invoice_number,
                :status, :is_printed, :is_delivered, :invoice_number, CAST(:totals AS jsonb), :sales_order_id,
                NOW(), NOW()
            )
        """),
        {
            "id": ls_id,
            "tenant_id": tenant_id,
            "delivery_note_number": delivery_note_number,
            **payload.model_dump(exclude={"positionen"}),
            "totals": totals_json,
        }
    )
    
    # Insert positions
    for pos in payload.positionen:
        pos_id = uuid7()
        listenpreis = pos.listenpreis or Decimal("0")
        rabatt = pos.rabatt or Decimal("0")
        menge = pos.menge
        
        netto_preis = listenpreis * (Decimal("1") - rabatt / Decimal("100"))
        netto_betrag = netto_preis * menge
        
        db.execute(
            text("""
                INSERT INTO domain_sales.delivery_note_positions (
                    id, delivery_note_id, pos_nr, artikel_id, artikel_nr, bezeichnung, bezeichnung2,
                    menge, einheit, listenpreis, rabatt, art, netto_preis, netto_betrag,
                    niederlassung, lagerhalle, lagerfach, charge, serien_nr, erloskonto, mwst_prozent,
                    kontrakt_nr, skontierf, fremdware, gef_punkt, na_bio, muster_nr, strecke, zus_beleg, anerken,
                    created_at, updated_at
                ) VALUES (
                    :id, :delivery_note_id, :pos_nr, :artikel_id, :artikel_nr, :bezeichnung, :bezeichnung2,
                    :menge, :einheit, :listenpreis, :rabatt, :art, :netto_preis, :netto_betrag,
                    :niederlassung, :lagerhalle, :lagerfach, :charge, :serien_nr, :erloskonto, :mwst_prozent,
                    :kontrakt_nr, :skontierf, :fremdware, :gef_punkt, :na_bio, :muster_nr, :strecke, :zus_beleg, :anerken,
                    NOW(), NOW()
                )
            """),
            {
                "id": pos_id,
                "delivery_note_id": ls_id,
                "netto_preis": netto_preis,
                "netto_betrag": netto_betrag,
                **pos.model_dump(),
            }
        )
    
    try:
        sync_movements_for_delivery_note(
            db=db,
            tenant_id=tenant_id,
            delivery_note_id=ls_id,
            delivery_note_number=delivery_note_number,
            positions=[pos.model_dump() for pos in payload.positionen],
            user_id=_get_user_id_from_request(request),
        )
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Kontrakt-Movement-Sync fehlgeschlagen", exc_info=True)

    db.commit()
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    positions = _list_positions(db, ls_id)
    
    return DeliveryNote(
        **dict(row),
        positionen=[DeliveryNotePosition(**dict(p)) for p in positions]
    )


@router.get("/{ls_id}", response_model=DeliveryNote, summary="Delivery note abrufen")
async def get_delivery_note(
    ls_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get a delivery note by ID."""
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    positions = _list_positions(db, ls_id)
    
    return DeliveryNote(
        **dict(row),
        positionen=[DeliveryNotePosition(**dict(p)) for p in positions]
    )


@router.put("/{ls_id}", response_model=DeliveryNote, summary="Delivery note aktualisieren")
async def update_delivery_note(
    ls_id: str,
    payload: DeliveryNoteUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update a delivery note. When status is draft and positionen is provided, positions are replaced (Option A)."""
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    if row["status"] != "draft" and payload.positionen is not None:
        raise HTTPException(
            status_code=400,
            detail="Positionen können nur bei Entwurf (draft) geändert werden.",
        )

    # Optional: Replace positions (only when draft and positionen is provided)
    if payload.positionen is not None and row["status"] == "draft":
        db.execute(
            text("DELETE FROM domain_sales.delivery_note_positions WHERE delivery_note_id = :id"),
            {"id": ls_id},
        )
        netto = Decimal("0")
        mwst = Decimal("0")
        for pos in payload.positionen:
            listenpreis = pos.listenpreis or Decimal("0")
            rabatt = pos.rabatt or Decimal("0")
            menge = pos.menge
            mwst_prozent = pos.mwst_prozent or Decimal("19")
            netto_preis = listenpreis * (Decimal("1") - rabatt / Decimal("100"))
            netto_betrag = netto_preis * menge
            mwst_betrag = netto_betrag * mwst_prozent / Decimal("100")
            netto += netto_betrag
            mwst += mwst_betrag
            pos_id = uuid7()
            db.execute(
                text("""
                    INSERT INTO domain_sales.delivery_note_positions (
                        id, delivery_note_id, pos_nr, artikel_id, artikel_nr, bezeichnung, bezeichnung2,
                        menge, einheit, listenpreis, rabatt, art, netto_preis, netto_betrag,
                        niederlassung, lagerhalle, lagerfach, charge, serien_nr, erloskonto, mwst_prozent,
                        kontrakt_nr, skontierf, fremdware, gef_punkt, na_bio, muster_nr, strecke, zus_beleg, anerken,
                        created_at, updated_at
                    ) VALUES (
                        :id, :delivery_note_id, :pos_nr, :artikel_id, :artikel_nr, :bezeichnung, :bezeichnung2,
                        :menge, :einheit, :listenpreis, :rabatt, :art, :netto_preis, :netto_betrag,
                        :niederlassung, :lagerhalle, :lagerfach, :charge, :serien_nr, :erloskonto, :mwst_prozent,
                        :kontrakt_nr, :skontierf, :fremdware, :gef_punkt, :na_bio, :muster_nr, :strecke, :zus_beleg, :anerken,
                        NOW(), NOW()
                    )
                """),
                {
                    "id": pos_id,
                    "delivery_note_id": ls_id,
                    "netto_preis": netto_preis,
                    "netto_betrag": netto_betrag,
                    **pos.model_dump(),
                },
            )
        brutto = netto + mwst
        totals = {"netto": float(netto), "mwst": float(mwst), "brutto": float(brutto)}
        db.execute(
            text("""
                UPDATE domain_sales.delivery_notes
                SET totals = CAST(:totals AS jsonb), updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {"id": ls_id, "tenant_id": tenant_id, "totals": json.dumps(totals)},
        )

    # Build header update (exclude positionen)
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if k != "positionen" and v is not None}
    if updates:
        set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
        updates["id"] = ls_id
        updates["tenant_id"] = tenant_id
        db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                UPDATE domain_sales.delivery_notes
                SET {set_clause}, updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            updates,
        )

    db.commit()
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    positions = _list_positions(db, ls_id)
    return DeliveryNote(
        **dict(row),
        positionen=[DeliveryNotePosition(**dict(p)) for p in positions],
    )


@router.delete("/{ls_id}", status_code=204, response_class=Response, response_model=None, summary="Delivery note löschen")
async def delete_delivery_note(
    ls_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete a delivery note. Only draft delivery notes can be deleted."""
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)

    if row["status"] != "draft":
        raise HTTPException(
            status_code=400,
            detail="Nur Entwürfe können gelöscht werden. Gebuchte Lieferscheine können nicht gelöscht werden.",
        )

    # Positionen zuerst löschen (FK-Constraint)
    db.execute(
        text("DELETE FROM domain_sales.delivery_note_positions WHERE delivery_note_id = :id"),
        {"id": ls_id},
    )
    db.execute(
        text("DELETE FROM domain_sales.delivery_notes WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": ls_id, "tenant_id": tenant_id},
    )
    db.commit()


@router.post("/{ls_id}/post", response_model=DeliveryNote, summary="Delivery note erstellen")
async def post_delivery_note(
    ls_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Post (book) a delivery note."""
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    
    if row["status"] != "draft":
        raise HTTPException(status_code=400, detail="Only draft delivery notes can be posted")
    
    db.execute(
        text("""
            UPDATE domain_sales.delivery_notes
            SET status = 'posted', updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": ls_id, "tenant_id": tenant_id}
    )
    db.flush()

    positions = _list_positions(db, ls_id)
    ls_number = row.get("ls_number") or row.get("delivery_note_number") or ls_id
    try:
        SalesPostingService(db, tenant_id).book_warenabgang(
            delivery_note_id=ls_id,
            delivery_note_number=ls_number,
            positions=positions,
            delivery_date=row.get("delivery_date") or row.get("created_at"),
        )
    except Exception:  # noqa: BLE001 — JWT decode failed; caller handles None return
        pass  # booking failure must not block the status transition

    db.commit()

    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    positions = _list_positions(db, ls_id)

    return DeliveryNote(
        **dict(row),
        positionen=[DeliveryNotePosition(**dict(p)) for p in positions]
    )


@router.post("/{ls_id}/print", summary="Delivery note drucken",
    response_model=None
)
async def print_delivery_note(
    ls_id: str,
    attestation: Optional[str] = Query(None, description="Reason for printing (required if already posted)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """Print a delivery note (with attestation if already posted)."""
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    
    # If already posted, require attestation
    if row["status"] in ("posted", "printed", "delivered") and not attestation:
        raise HTTPException(
            status_code=400,
            detail="Attestation reason required for printing posted delivery notes"
        )
    
    # Create attestation record if needed
    if attestation:
        attestation_id = uuid7()
        db.execute(
            text("""
                INSERT INTO domain_audit.attestations (
                    id, tenant_id, entity_type, entity_id, action, reason, created_by, created_at
                ) VALUES (
                    :id, :tenant_id, 'delivery_note', :entity_id, 'print', :reason, :created_by, NOW()
                )
            """),
            {
                "id": attestation_id,
                "tenant_id": tenant_id,
                "entity_id": ls_id,
                "reason": attestation,
                "created_by": _get_user_id_from_request(request) or "system",
            }
        )
    
    # Update delivery note
    db.execute(
        text("""
            UPDATE domain_sales.delivery_notes 
            SET is_printed = TRUE, status = 'printed', updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": ls_id, "tenant_id": tenant_id}
    )
    db.commit()
    
    return {"ok": True, "message": "Delivery note printed"}


@router.post("/{ls_id}/ship", response_model=DeliveryNote, summary="Delivery note ship")
async def ship_delivery_note(
    ls_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lieferschein versenden — posted/printed → shipped."""
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    if row["status"] not in ("posted", "printed"):
        raise HTTPException(status_code=400, detail=f"Nur gebuchte/gedruckte Lieferscheine können versandt werden (Status: {row['status']})")
    db.execute(
        text("UPDATE domain_sales.delivery_notes SET status = 'shipped', updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": ls_id, "tenant_id": tenant_id},
    )
    db.commit()
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    positions = _list_positions(db, ls_id)
    return DeliveryNote(**dict(row), positionen=[DeliveryNotePosition(**dict(p)) for p in positions])


@router.post("/{ls_id}/deliver", response_model=DeliveryNote, summary="Delivery note deliver")
async def deliver_delivery_note(
    ls_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lieferung bestätigen — shipped → delivered."""
    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    if row["status"] != "shipped":
        raise HTTPException(status_code=400, detail=f"Nur versandte Lieferscheine können als geliefert markiert werden (Status: {row['status']})")
    db.execute(
        text("UPDATE domain_sales.delivery_notes SET status = 'delivered', updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": ls_id, "tenant_id": tenant_id},
    )
    db.commit()

    # O2C completion: wenn Auftrag vollständig geliefert → Auftrag auf geliefert setzen
    order_id = row.get("sales_order_id")
    if order_id:
        try:
            from app.services.sales_match_service import SalesMatchService
            match = SalesMatchService(db, tenant_id).match(order_id)
            if match.get("vollstaendig_geliefert"):
                db.execute(
                    text("UPDATE domain_crm.sales_orders SET status = 'geliefert', updated_at = NOW() WHERE id = :oid AND tenant_id = :tid"),
                    {"oid": order_id, "tid": tenant_id},
                )
                db.commit()
        except Exception:  # noqa: BLE001 — order status update is non-blocking
            pass

    row = _get_delivery_note_or_404(db, ls_id, tenant_id)
    positions = _list_positions(db, ls_id)
    return DeliveryNote(**dict(row), positionen=[DeliveryNotePosition(**dict(p)) for p in positions])


@router.get("", response_model=list[DeliveryNote], summary="Delivery notes auflisten")
async def list_delivery_notes(
    customer_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List delivery notes."""
    query = """
        SELECT * FROM domain_sales.delivery_notes 
        WHERE tenant_id = :tenant_id
    """
    params = {"tenant_id": tenant_id}
    
    if customer_id:
        query += " AND customer_id = :customer_id"
        params["customer_id"] = customer_id
    
    if status_filter:
        query += " AND status = :status"
        params["status"] = status_filter
    
    query += " ORDER BY delivery_date DESC, delivery_note_number DESC LIMIT :limit OFFSET :skip"
    params["limit"] = limit
    params["skip"] = skip
    
    rows = db.execute(text(query), params).mappings().all()
    
    result = []
    for row in rows:
        positions = _list_positions(db, row["id"])
        result.append(
            DeliveryNote(
                **dict(row),
                positionen=[DeliveryNotePosition(**dict(p)) for p in positions]
            )
        )
    
    return result


@router.get("/last", response_model=Optional[DeliveryNote], summary="Last delivery note abrufen")
async def get_last_delivery_note(
    operator_id: Optional[str] = Query(None, description="Filter by operator ID (user who created the delivery note)"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get the last delivery note for a user/customer (for 'Wie vorheriger Beleg' functionality)."""
    query = """
        SELECT * FROM domain_sales.delivery_notes 
        WHERE tenant_id = :tenant_id
    """
    params = {"tenant_id": tenant_id}
    
    if operator_id:
        query += " AND operator_id = :operator_id"
        params["operator_id"] = operator_id
    
    if customer_id:
        query += " AND customer_id = :customer_id"
        params["customer_id"] = customer_id
    
    query += " ORDER BY created_at DESC LIMIT 1"
    
    row = db.execute(text(query), params).mappings().first()
    
    if not row:
        return None
    
    positions = _list_positions(db, row["id"])
    return DeliveryNote(
        **dict(row),
        positionen=[DeliveryNotePosition(**dict(p)) for p in positions]
    )


@router.post("/{ls_id}/create-invoice", response_model=SalesDeliveryNotesOut, status_code=201, summary="Invoice from delivery anlegen")
async def create_invoice_from_delivery(
    ls_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a sales invoice from a posted delivery note (Dokumentenfluss LS → RE)."""
    row = db.execute(
        text("SELECT * FROM domain_sales.delivery_notes WHERE id = :id AND tenant_id = :tid"),
        {"id": ls_id, "tid": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Lieferschein nicht gefunden")
    if row.get("status") not in ("posted", "printed", "gebucht"):
        raise HTTPException(status_code=400, detail="Lieferschein muss gebucht/gedruckt sein, bevor eine Rechnung erstellt werden kann")

    positions = _list_positions(db, ls_id)
    total = sum(Decimal(str(p.get("netto_betrag") or 0)) for p in positions)
    inv_id = uuid7()
    inv_nr = f"RE-{row.get('ls_nummer', ls_id[:8])}"

    db.execute(text("CREATE SCHEMA IF NOT EXISTS domain_erp"))
    db.execute(
        text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, description,
             source, status, total_debit, total_credit, reference, created_at, updated_at)
            VALUES (:id, :tid, :en, NOW(), NOW(), :desc,
                    'sales_invoice', 'posted', :total, :total, :ref, NOW(), NOW())
        """),
        {
            "id": inv_id, "tid": tenant_id,
            "en": inv_nr, "desc": f"Rechnung aus Lieferschein {row.get('ls_nummer', '')}",
            "total": total, "ref": inv_nr,
        },
    )

    db.execute(
        text("""
            UPDATE domain_sales.delivery_notes
            SET status = 'invoiced', updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": ls_id, "tenant_id": tenant_id},
    )
    db.commit()

    # SALES-DN-INV-OP-001: Debitoren-OP + Document-Store Eintrag (Belegbruch schliessen)
    try:
        from datetime import date as _date
        import uuid as _uuid
        today = _date.today().isoformat()
        due = _date.today().replace(day=min(_date.today().day + 30, 28)).isoformat()
        db.execute(text("""
            INSERT INTO domain_erp.offene_posten
                (id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, faelligkeit,
                 betrag, offen, kunde_id, op_status)
            VALUES (:id, :tid, 'debitoren', :rnr, :rdat, :dat, :faell,
                    :betrag, :betrag, :kid, 'offen')
            ON CONFLICT DO NOTHING
        """), {
            "id": str(_uuid.uuid4()), "tid": tenant_id, "rnr": inv_nr,
            "rdat": today, "dat": today, "faell": due,
            "betrag": float(total),
            "kid": row.get("customer_id") or "",
        })
        db.commit()
    except Exception:  # noqa: BLE001 — OP-Anlage nicht kritisch
        pass
    try:
        repo = get_repository(db)
        save_to_store("sales_invoice", inv_nr, {
            "id": str(inv_id), "number": inv_nr,
            "deliveryNoteId": ls_id, "customerId": row.get("customer_id") or "",
            "totalGross": float(total), "status": "GEBUCHT",
            "tenantId": tenant_id,
        }, repo)
    except Exception:  # noqa: BLE001 — Store-Eintrag nicht kritisch
        pass

    return {
        "ok": True,
        "invoice_id": inv_id,
        "invoice_number": inv_nr,
        "delivery_note_id": ls_id,
        "total": float(total),
    }

